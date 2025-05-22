from django.http import JsonResponse
from ..decorators import endpoint_enabled, safe_json_response

from utils.dynamic_import import get_query_class  # importa o helper
LineageStats = get_query_class("LineageStats")  # carrega a classe certa com base no .env

from apps.main.home.decorator import conditional_otp_required
from django.contrib.admin.views.decorators import staff_member_required
from ..models import Apoiador
from apps.lineage.shop.models import ShopPurchase, PromotionCode
from django.shortcuts import render, redirect
from django.contrib import messages
from ..forms import ApoiadorForm
from django.db.models import Sum
from django.utils import timezone

from ..forms import SolicitarComissaoForm, ImagemApoiadorForm
from ..utils.apoiador import pagar_comissao, calcular_valor_disponivel
from decimal import Decimal


@endpoint_enabled('players_online')
@safe_json_response
def players_online(request):
    return LineageStats.players_online()


@endpoint_enabled('top_pvp')
@safe_json_response
def top_pvp(request):
    limit = int(request.GET.get("limit", 10))
    return LineageStats.top_pvp(limit=limit)


@endpoint_enabled('top_pk')
@safe_json_response
def top_pk(request):
    limit = int(request.GET.get("limit", 10))
    return LineageStats.top_pk(limit=limit)


@endpoint_enabled('top_clan')
@safe_json_response
def top_clan(request):
    limit = int(request.GET.get("limit", 10))
    return LineageStats.top_clans(limit=limit)


@endpoint_enabled('top_rich')
@safe_json_response
def top_rich(request):
    limit = int(request.GET.get("limit", 10))
    return LineageStats.top_adena(limit=limit)


@endpoint_enabled('top_online')
@safe_json_response
def top_online(request):
    limit = int(request.GET.get("limit", 10))
    return LineageStats.top_online(limit=limit)


@endpoint_enabled('top_level')
@safe_json_response
def top_level(request):
    limit = int(request.GET.get("limit", 10))
    return LineageStats.top_level(limit=limit)


@endpoint_enabled('olympiad_ranking')
@safe_json_response
def olympiad_ranking(request):
    return LineageStats.olympiad_ranking()


@endpoint_enabled('olympiad_all_heroes')
@safe_json_response
def olympiad_all_heroes(request):
    return LineageStats.olympiad_all_heroes()


@endpoint_enabled('olympiad_current_heroes')
@safe_json_response
def olympiad_current_heroes(request):
    return LineageStats.olympiad_current_heroes()


@endpoint_enabled('grandboss_status')
@safe_json_response
def grandboss_status(request):
    return LineageStats.grandboss_status()


@endpoint_enabled('siege')
@safe_json_response
def siege(request):
    return LineageStats.siege()


@endpoint_enabled('siege_participants')
@safe_json_response
def siege_participants(request, castle_id):
    if castle_id not in range(1, 10):
        return JsonResponse({'error': 'castle_id deve ser um valor entre 1 e 9'}, status=400)
    return LineageStats.siege_participants(castle_id=castle_id)


@endpoint_enabled('boss_jewel_locations')
@safe_json_response
def boss_jewel_locations(request):
    jewel_ids = request.GET.get("ids", "")
    
    if not jewel_ids:
        return JsonResponse({"error": "Missing jewel item IDs"}, status=400)
    
    try:
        jewel_ids_list = [int(id) for id in jewel_ids.split(',')]
    except ValueError:
        return JsonResponse({"error": "Invalid ID format"}, status=400)
    
    allowed_ids = [6656, 6657, 6658, 6659, 6660, 6661, 8191]
    if not all(id in allowed_ids for id in jewel_ids_list):
        return JsonResponse({"error": "Invalid jewel item ID(s)"}, status=400)
    
    return LineageStats.boss_jewel_locations(boss_jewel_ids=jewel_ids_list)


@conditional_otp_required
def painel_apoiador(request):
    try:
        apoiador = Apoiador.objects.get(user=request.user)
    except Apoiador.DoesNotExist:
        return render(request, 'apoiadores/nao_apoiador.html')

    # Status expirado permite reenviar o formulário
    if apoiador.status == 'expirado':
        return render(request, 'apoiadores/expirado.html', {'apoiador': apoiador})

    if apoiador.status == 'pendente':
        return render(request, 'apoiadores/pendente.html', {'apoiador': apoiador})
    elif apoiador.status == 'rejeitado':
        return render(request, 'apoiadores/rejeitado.html', {'apoiador': apoiador})
    elif apoiador.status != 'aprovado':
        return render(request, 'apoiadores/nao_apoiador.html')

    # Painel de apoiador aprovado
    compras = (
        ShopPurchase.objects
        .filter(apoiador=apoiador)
        .select_related('user')
        .only('user__username', 'character_name', 'total_pago', 'data_compra')
        .order_by('-data_compra')
    )

    total_vendas = compras.aggregate(total=Sum('total_pago'))['total'] or 0
    total_usuarios = compras.values('user').distinct().count()

    try:
        cupom = PromotionCode.objects.get(apoiador=apoiador, ativo=True)
    except PromotionCode.DoesNotExist:
        cupom = None

    return render(request, 'apoiadores/painel.html', {
        'apoiador': apoiador,
        'compras': compras,
        'total_vendas': total_vendas,
        'total_usuarios': total_usuarios,
        'cupom': cupom
    })


@conditional_otp_required
def formulario_apoiador(request):
    try:
        apoiador = Apoiador.objects.get(user=request.user)
        if apoiador.status == 'aprovado' or apoiador.status == 'pendente':
            messages.info(request, "Você já possui uma solicitação ativa.")
            return redirect('server:painel_apoiador')
    except Apoiador.DoesNotExist:
        apoiador = None

    if request.method == "POST":
        form = ApoiadorForm(request.POST, request.FILES, instance=apoiador)

        if form.is_valid():
            novo_apoiador = form.save(commit=False)
            novo_apoiador.user = request.user
            novo_apoiador.status = 'pendente'  # Sempre reinicia como pendente
            novo_apoiador.save()

            messages.success(request, "Sua nova solicitação foi enviada com sucesso! Aguarde análise.")
            return redirect('server:painel_apoiador')
        else:
            messages.error(request, "Ocorreu um erro ao enviar a solicitação. Verifique os dados.")
    else:
        form = ApoiadorForm(instance=apoiador)

    return render(request, 'apoiadores/formulario_apoiador.html', {'form': form})


@staff_member_required
def painel_staff(request):
    if request.method == 'POST':
        apoiador_id = request.POST.get('apoiador_id')
        acao = request.POST.get('acao')
        desconto_percentual = request.POST.get('desconto_percentual')

        try:
            apoiador = Apoiador.objects.get(id=apoiador_id)

            if acao == 'aceitar':
                apoiador.status = 'aprovado'
                apoiador.save()

                if desconto_percentual:
                    desconto_percentual = float(desconto_percentual)
                else:
                    messages.error(request, 'A porcentagem do cupom é obrigatória.')
                    return redirect('server:painel_staff')

                promocao, created = PromotionCode.objects.get_or_create(
                    apoiador=apoiador,
                    defaults={
                        'codigo': f"{str(apoiador.nome_publico).upper().replace(' ', '_').replace('-', '_')}-{int(desconto_percentual)}",
                        'desconto_percentual': desconto_percentual,
                        'ativo': True,
                        'validade': timezone.now() + timezone.timedelta(days=30)
                    }
                )

                # Se o cupom já existia, atualize o desconto
                if not created:
                    promocao.desconto_percentual = desconto_percentual
                    promocao.validade = timezone.now() + timezone.timedelta(days=30)
                    promocao.save()

                messages.success(request, f'Apoiador {apoiador.nome_publico} aprovado e cupom gerado ou atualizado!')

            elif acao == 'rejeitar':
                # Alterar o status para 'rejeitado'
                apoiador.status = 'rejeitado'
                apoiador.save()

                messages.info(request, f'Apoiador {apoiador.nome_publico} rejeitado.')

        except Apoiador.DoesNotExist:
            messages.error(request, 'Apoiador não encontrado.')

    pedidos_pendentes = Apoiador.objects.filter(status='pendente')
    return render(request, 'apoiadores/painel_staff.html', {'pedidos_pendentes': pedidos_pendentes})


@conditional_otp_required
def solicitar_comissao(request):
    try:
        apoiador = Apoiador.objects.get(user=request.user)
    except Apoiador.DoesNotExist:
        return redirect('server:painel_apoiador')

    if apoiador.status != 'aprovado':
        messages.error(request, "Seu cadastro não está aprovado para solicitar comissão.")
        return redirect('server:painel_apoiador')

    # Valor disponível para saque
    valor_disponivel = calcular_valor_disponivel(apoiador)

    if request.method == 'POST':
        form = SolicitarComissaoForm(request.POST)
        if form.is_valid():
            valor = form.cleaned_data['valor']

            if valor > valor_disponivel:
                messages.error(request, f'O valor solicitado excede o disponível (R${valor_disponivel}).')
            elif valor <= 0:
                messages.error(request, "O valor solicitado deve ser maior que zero.")
            else:
                pagar_comissao(apoiador, Decimal(valor))
                messages.success(request, f'Comissão de R${valor} solicitada com sucesso!')
                return redirect('server:painel_apoiador')
    else:
        form = SolicitarComissaoForm()

    return render(request, 'apoiadores/solicitar_comissao.html', {
        'form': form,
        'valor_disponivel': valor_disponivel
    })


@conditional_otp_required
def editar_imagem_apoiador(request):
    try:
        apoiador = Apoiador.objects.get(user=request.user)
    except Apoiador.DoesNotExist:
        return redirect('server:painel_apoiador')  # ou uma página de erro

    if request.method == 'POST':
        form = ImagemApoiadorForm(request.POST, request.FILES, instance=apoiador)
        if form.is_valid():
            form.save()
            return redirect('server:painel_apoiador')
    else:
        form = ImagemApoiadorForm(instance=apoiador)

    return render(request, 'apoiadores/editar_imagem.html', {'form': form})
