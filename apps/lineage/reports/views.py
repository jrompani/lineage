import json

from django.shortcuts import render
from django.db.models import Sum, Count
from django.contrib.admin.views.decorators import staff_member_required
from django.utils import timezone
from django.utils.timezone import now, timedelta

from apps.lineage.auction.models import Auction, Bid
from apps.lineage.inventory.models import InventoryLog
from apps.lineage.shop.models import ShopPurchase, ShopItem, ShopPackage, PromotionCode, Cart


@staff_member_required
def relatorio_movimentacoes_inventario(request):
    dias = 15
    data_inicio = now() - timedelta(days=dias)

    logs = InventoryLog.objects.filter(timestamp__gte=data_inicio)

    # Agrupamento por dia
    agrupado_por_dia = (
        logs.extra(select={'dia': "DATE(timestamp)"})
        .values('dia', 'acao')
        .annotate(total=Sum('quantity'))
        .order_by('dia')
    )

    # Coleta das datas únicas
    dias_labels = sorted(set(log['dia'] for log in agrupado_por_dia))
    dias_labels_str = [str(dia) for dia in dias_labels]

    acoes = ['RETIROU_DO_JOGO', 'INSERIU_NO_JOGO', 'TROCA_ENTRE_PERSONAGENS', 'RECEBEU_TROCA', 'BAG_PARA_INVENTARIO']
    dados_por_acao = {acao: [0] * len(dias_labels) for acao in acoes}

    for log in agrupado_por_dia:
        dia = log['dia']
        idx = dias_labels.index(dia)
        acao = log['acao']
        if acao in dados_por_acao:
            dados_por_acao[acao][idx] = int(log['total'])

    # Itens mais trocados
    itens_trocados = (
        logs.filter(acao='TROCA_ENTRE_PERSONAGENS')
        .values('item_name')
        .annotate(total_trocado=Sum('quantity'))
        .order_by('-total_trocado')[:5]
    )

    # Itens mais movimentados
    itens_movimentados = (
        logs.values('item_name')
        .annotate(total_movimentado=Sum('quantity'))
        .order_by('-total_movimentado')[:5]
    )

    total_retirado = sum(dados_por_acao['RETIROU_DO_JOGO'])
    total_inserido = sum(dados_por_acao['INSERIU_NO_JOGO'])
    total_troca = sum(dados_por_acao['TROCA_ENTRE_PERSONAGENS'])
    total_recebido = sum(dados_por_acao['RECEBEU_TROCA'])
    total_bag_para_inventario = sum(dados_por_acao['BAG_PARA_INVENTARIO'])

    contexto = {
        'labels': json.dumps(dias_labels_str),
        'retirados': json.dumps(dados_por_acao['RETIROU_DO_JOGO']),
        'inseridos': json.dumps(dados_por_acao['INSERIU_NO_JOGO']),
        'trocados': json.dumps(dados_por_acao['TROCA_ENTRE_PERSONAGENS']),
        'recebidos': json.dumps(dados_por_acao['RECEBEU_TROCA']),
        'bag_para_inventario': json.dumps(dados_por_acao['BAG_PARA_INVENTARIO']),
        'itens_trocados': itens_trocados,
        'itens_movimentados': itens_movimentados,
        'total_retirado': total_retirado,
        'total_inserido': total_inserido,
        'total_troca': total_troca,
        'total_recebido': total_recebido,
        'total_bag_para_inventario': total_bag_para_inventario,
    }

    return render(request, 'reports/relatorio_movimentacoes_inventario.html', contexto)


@staff_member_required
def relatorio_leiloes(request):
    # Leilões Ativos
    leiloes_ativos = Auction.objects.filter(end_time__gt=now(), status='pending').order_by('-end_time')

    # Histórico de Lances
    lances = Bid.objects.select_related('auction', 'bidder').order_by('-created_at')

    # Status dos Leilões
    leiloes_pendentes = Auction.objects.filter(status='pending').count()
    leiloes_fechados = Auction.objects.filter(status='finished').count()
    leiloes_expirados = Auction.objects.filter(status='expired').count()
    leiloes_cancelados = Auction.objects.filter(status='cancelled').count()

    # Leilões mais Populares (baseado no número de lances)
    leiloes_populares = Auction.objects.annotate(num_lances=Count('bids')).order_by('-num_lances')[:5]

    # Dados para gráficos
    status_labels = ['Pendentes', 'Finalizados', 'Expirados', 'Cancelados']
    status_values = [leiloes_pendentes, leiloes_fechados, leiloes_expirados, leiloes_cancelados]

    # Leilões mais populares - Top 5 com o número de lances
    leiloes_populares_names = [leilao.item_name for leilao in leiloes_populares]
    leiloes_populares_lances = [leilao.num_lances for leilao in leiloes_populares]

    contexto = {
        'leiloes_ativos': leiloes_ativos,
        'lances': lances,
        'leiloes_pendentes': leiloes_pendentes,
        'leiloes_fechados': leiloes_fechados,
        'leiloes_expirados': leiloes_expirados,
        'leiloes_cancelados': leiloes_cancelados,
        'leiloes_populares': leiloes_populares,
        'status_labels': status_labels,
        'status_values': status_values,
        'leiloes_populares_names': leiloes_populares_names,
        'leiloes_populares_lances': leiloes_populares_lances,
    }

    return render(request, 'reports/relatorio_leiloes.html', contexto)


@staff_member_required
def relatorio_compras(request):
    # Total de Compras
    total_compras = ShopPurchase.objects.count()
    total_pago = ShopPurchase.objects.aggregate(Sum('total_pago'))['total_pago__sum'] or 0

    # Carrinhos Abandonados
    carrinhos_abandonados = Cart.objects.filter(
        user__isnull=False
    ).exclude(
        user__in=ShopPurchase.objects.values('user')
    ).count()

    # Itens Mais Vendidos - Utilizando prefetch_related para otimizar a consulta
    itens_mais_vendidos = ShopItem.objects.annotate(
        quantidade_vendida=Sum('cartitem__quantidade')
    ).order_by('-quantidade_vendida')[:5]

    # Pacotes Populares
    pacotes_populares = ShopPackage.objects.annotate(
        quantidade_vendida=Sum('cartpackage__quantidade')
    ).order_by('-quantidade_vendida')[:5]

    # Promoções Utilizadas
    promocoes_utilizadas = PromotionCode.objects.annotate(
        quantidade_utilizada=Count('shoppurchase')
    ).order_by('-quantidade_utilizada')[:5]

    # Receita por Período (Última Semana)
    data_inicio = timezone.now() - timezone.timedelta(weeks=1)
    receita_periodo = ShopPurchase.objects.filter(
        data_compra__gte=data_inicio
    ).aggregate(Sum('total_pago'))['total_pago__sum'] or 0

    # Prepare os dados para o template
    contexto = {
        'total_compras': total_compras,
        'total_pago': total_pago,
        'carrinhos_abandonados': carrinhos_abandonados,
        'itens_mais_vendidos': [{'nome': item.nome, 'quantidade_vendida': item.quantidade_vendida or 0} for item in itens_mais_vendidos],
        'pacotes_populares': [{'nome': pacote.nome, 'quantidade_vendida': pacote.quantidade_vendida or 0} for pacote in pacotes_populares],
        'promocoes_utilizadas': [{'codigo': promocao.codigo, 'quantidade_utilizada': promocao.quantidade_utilizada} for promocao in promocoes_utilizadas],
        'receita_periodo': receita_periodo,
    }

    return render(request, 'reports/relatorio_compras.html', contexto)
