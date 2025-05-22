from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.main.home.models import User
from apps.lineage.wallet.models import Wallet, TransacaoWallet
from core.models import BaseModel
from .choices import *


class PedidoPagamento(BaseModel):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_("User"))
    valor_pago = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_("Amount Paid"))
    moedas_geradas = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_("Coins Generated"))
    metodo = models.CharField(max_length=100, verbose_name=_("Payment Method"))
    status = models.CharField(max_length=20, default='PENDENTE', verbose_name=_("Status"))  # CONFIRMADO, FALHOU...
    data_criacao = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))

    def confirmar_pagamento(self):
        if self.status != 'CONFIRMADO':
            self.status = 'CONFIRMADO'
            self.save()

            wallet, wallet_created = Wallet.objects.get_or_create(usuario=self.usuario)

            TransacaoWallet.objects.create(
                wallet=wallet,
                tipo='ENTRADA',
                valor=self.moedas_geradas,
                descricao=_("Purchase of coins via ADMINISTRATOR") + f" ('{self.metodo}')",
                origem=_("Payment System"),
                destino=_("Wallet")
            )

            wallet.saldo += self.moedas_geradas
            wallet.save()

    def __str__(self):
        return f"Pedido #{self.id} - {self.usuario.username} - {self.status}"

    class Meta:
        verbose_name = _("Payment Request")
        verbose_name_plural = _("Payment Requests")


class Pagamento(BaseModel):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_("User"))
    valor = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_("Value"))
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='pending', verbose_name=_("Status"))
    transaction_code = models.CharField(max_length=100, null=True, blank=True, verbose_name=_("Transaction Code"))
    pedido_pagamento = models.OneToOneField(
        PedidoPagamento,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("Linked Payment Request")
    )
    data_criacao = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))

    def __str__(self):
        return f"Pagamento {self.id} - {self.status}"

    class Meta:
        verbose_name = _("Payment")
        verbose_name_plural = _("Payments")


class WebhookLog(models.Model):
    tipo = models.CharField(max_length=100, verbose_name=_("Type"))
    data_id = models.CharField(max_length=100, verbose_name=_("Data ID"))
    payload = models.JSONField(verbose_name=_("Payload"))
    recebido_em = models.DateTimeField(auto_now_add=True, verbose_name=_("Received At"))

    class Meta:
        verbose_name = _("Webhook Log")
        verbose_name_plural = _("Webhook Logs")

    def __str__(self):
        return f"{self.tipo} - {self.data_id}"
