from apps.lineage.payment.models import PedidoPagamento, Pagamento


def pedidos_pagamentos_resumo():
    pedidos = PedidoPagamento.objects.all().order_by('-data_criacao')
    relatorio = []

    for pedido in pedidos:
        pagamento = Pagamento.objects.filter(pedido_pagamento=pedido).first()
        relatorio.append({
            'pedido_id': pedido.id,
            'usuario': pedido.usuario.username,
            'valor_pago': pedido.valor_pago,
            'moedas_geradas': pedido.moedas_geradas,
            'status_pedido': pedido.status,
            'status_pagamento': pagamento.status if pagamento else 'Sem Pagamento',
            'metodo': pedido.metodo,
            'data': pedido.data_criacao,
        })

    return relatorio
