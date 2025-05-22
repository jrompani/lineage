from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
import mercadopago
import stripe
from ..models import *
from django.http import HttpResponse
from apps.main.home.decorator import conditional_otp_required
from datetime import timedelta
from django.utils.timezone import now
from django.contrib import messages
from django.db import transaction
from utils.services import verificar_conquistas
from apps.main.home.models import PerfilGamer


stripe.api_key = settings.STRIPE_SECRET_KEY


@conditional_otp_required
def criar_ou_reaproveitar_pedido(request):
    if request.method == 'POST':
        try:
            valor = float(request.POST.get('valor'))
            if valor <= 0:
                return HttpResponse("Valor inválido", status=400)
        except (TypeError, ValueError):
            return HttpResponse("Valor inválido", status=400)

        metodo = request.POST.get('metodo')
        if metodo not in settings.METHODS_PAYMENTS:  # Expanda conforme necessário
            return HttpResponse("Método de pagamento inválido", status=400)
        
        if metodo == "MercadoPago" and not settings.MERCADO_PAGO_ACTIVATE_PAYMENTS:
            messages.error(request, "Método de pagamento desativado.")
            return redirect('payment:novo_pedido')
        
        if metodo == "Stripe" and not settings.STRIPE_ACTIVATE_PAYMENTS:
            messages.error(request, "Método de pagamento desativado.")
            return redirect('payment:novo_pedido')

        usuario = request.user
        duas_horas_atras = now() - timedelta(hours=2)

        with transaction.atomic():
            # Lock em todos os pedidos pendentes parecidos do usuário (para evitar criação duplicada)
            pedidos_similares = (
                PedidoPagamento.objects
                .select_for_update()
                .filter(
                    usuario=usuario,
                    valor_pago=valor,
                    metodo=metodo,
                    status='PENDENTE',
                    data_criacao__gte=duas_horas_atras
                )
            )

            pedido_existente = pedidos_similares.first()
            if pedido_existente:
                return redirect('payment:detalhes_pedido', pedido_id=pedido_existente.id)

            novo_pedido = PedidoPagamento.objects.create(
                usuario=usuario,
                valor_pago=valor,
                moedas_geradas=valor,
                metodo=metodo,
                status='PENDENTE'
            )

            perfil = PerfilGamer.objects.get(user=request.user)
            perfil.adicionar_xp(40)
            verificar_conquistas(request.user, request=request)

            return redirect('payment:detalhes_pedido', pedido_id=novo_pedido.id)

    return render(request, "payment/purchase.html")


@conditional_otp_required
def confirmar_pagamento(request, pedido_id):
    try:
        with transaction.atomic():
            pedido = PedidoPagamento.objects.select_for_update().get(id=pedido_id, usuario=request.user)

            if pedido.status != 'PENDENTE':
                return HttpResponse("Pedido já processado ou inválido.")

            pagamento = Pagamento.objects.filter(pedido_pagamento=pedido).first()
            if pagamento:
                if pedido.metodo == "MercadoPago" and pagamento.transaction_code:
                    sdk = mercadopago.SDK(settings.MERCADO_PAGO_ACCESS_TOKEN)
                    preference_response = sdk.preference().get(pagamento.transaction_code)

                    if preference_response.get("status") != 200:
                        return HttpResponse("Erro ao recuperar preferência de pagamento", status=500)

                    preference = preference_response.get("response", {})
                    return redirect(preference["init_point"])

                if pedido.metodo == "Stripe" and pagamento.transaction_code:
                    return redirect(f"https://checkout.stripe.com/pay/{pagamento.transaction_code}")

                return HttpResponse("Já existe um pagamento iniciado para este pedido.", status=400)

            pagamento = Pagamento.objects.create(
                usuario=request.user,
                valor=pedido.valor_pago,
                status="pending",
                pedido_pagamento=pedido
            )

            if pedido.metodo == "MercadoPago":
                sdk = mercadopago.SDK(settings.MERCADO_PAGO_ACCESS_TOKEN)
                preference_data = {
                    "items": [{
                        "title": "Moedas para o jogo",
                        "quantity": 1,
                        "currency_id": "BRL",
                        "unit_price": float(pedido.valor_pago),
                    }],
                    "back_urls": {
                        "success": settings.MERCADO_PAGO_SUCCESS_URL,
                        "failure": settings.MERCADO_PAGO_FAILURE_URL,
                    },
                    "auto_return": "approved",
                    "metadata": {"pagamento_id": pagamento.id}
                }

                preference_response = sdk.preference().create(preference_data)
                if preference_response.get("status") != 201:
                    return HttpResponse("Erro ao criar preferência de pagamento", status=500)

                preference = preference_response.get("response", {})
                pagamento.transaction_code = preference["id"]
                pagamento.save()

                perfil = PerfilGamer.objects.get(user=request.user)
                perfil.adicionar_xp(100)
                verificar_conquistas(request.user, request=request)

                return redirect(preference["init_point"])

            elif pedido.metodo == "Stripe":
                session = stripe.checkout.Session.create(
                    payment_method_types=['card'],
                    mode='payment',
                    line_items=[{
                        'price_data': {
                            'currency': 'brl',
                            'product_data': {'name': 'Moedas para o jogo'},
                            'unit_amount': int(pedido.valor_pago * 100),
                        },
                        'quantity': 1,
                    }],
                    success_url=settings.STRIPE_SUCCESS_URL + '?session_id={CHECKOUT_SESSION_ID}',
                    cancel_url=settings.STRIPE_FAILURE_URL,
                    metadata={"pagamento_id": pagamento.id}
                )

                pagamento.transaction_code = session.id
                pagamento.save()

                perfil = PerfilGamer.objects.get(user=request.user)
                perfil.adicionar_xp(100)
                verificar_conquistas(request.user, request=request)

                return redirect(session.url, code=303)

            return HttpResponse("Método de pagamento não suportado", status=400)

    except PedidoPagamento.DoesNotExist:
        return HttpResponse("Pedido não encontrado.", status=404)


@conditional_otp_required
def detalhes_pedido(request, pedido_id):
    pedido = get_object_or_404(PedidoPagamento, id=pedido_id, usuario=request.user)

    if pedido.status != 'PENDENTE':
        return HttpResponse("Pedido já processado ou inválido.")

    if request.method == 'POST':
        return redirect('payment:confirmar_pagamento', pedido_id=pedido.id)

    return render(request, "payment/detalhes_pedido.html", {"pedido": pedido})


@conditional_otp_required
def pedidos_pendentes(request):
    pedidos = PedidoPagamento.objects.filter(usuario=request.user, status='PENDENTE').order_by('-data_criacao')
    return render(request, "payment/pedidos_pendentes.html", {"pedidos": pedidos})


@conditional_otp_required
def cancelar_pedido(request, pedido_id):
    if request.method != 'POST':
        return HttpResponse("Método não permitido", status=405)

    pedido = get_object_or_404(PedidoPagamento, id=pedido_id, usuario=request.user)

    if pedido.status != 'PENDENTE':
        return HttpResponse("Este pedido não pode ser cancelado.", status=400)

    pedido.status = 'CANCELADO'
    pedido.save()

    messages.success(request, "Pedido cancelado com sucesso.")
    return redirect('payment:pedidos_pendentes')
