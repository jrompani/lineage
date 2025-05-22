from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.main.home.models import User
from core.models import BaseModel


class Wallet(BaseModel):
    usuario = models.OneToOneField(User, verbose_name=_("Usuário"), on_delete=models.CASCADE)
    saldo = models.DecimalField(_("Saldo"), max_digits=10, decimal_places=2, default=0.00)

    class Meta:
        verbose_name = _("Carteira")
        verbose_name_plural = _("Carteiras")

    def __str__(self):
        return f"Carteira de {self.usuario.username} - Saldo: R${self.saldo}"


class TransacaoWallet(BaseModel):
    TIPO = [
        ('ENTRADA', _("Entrada")),
        ('SAIDA', _("Saída")),
    ]

    wallet = models.ForeignKey(Wallet, verbose_name=_("Carteira"), on_delete=models.CASCADE, related_name='transacoes')
    tipo = models.CharField(_("Tipo"), max_length=10, choices=TIPO)
    valor = models.DecimalField(_("Valor"), max_digits=10, decimal_places=2)
    descricao = models.TextField(_("Descrição"), blank=True)
    data = models.DateTimeField(_("Data da Transação"), auto_now_add=True)
    origem = models.CharField(_("Origem"), max_length=100, blank=True)  # Ex: "Pix", "Venda"
    destino = models.CharField(_("Destino"), max_length=100, blank=True) # Ex: "Fulano", "MercadoPago"

    class Meta:
        verbose_name = _("Transação da Carteira")
        verbose_name_plural = _("Transações da Carteira")

    def __str__(self):
        return f"{self.tipo} de R${self.valor} - {self.data.strftime('%d/%m/%Y %H:%M')}"


class CoinConfig(BaseModel):
    nome = models.CharField(_("Nome da Moeda"), max_length=100)
    coin_id = models.PositiveIntegerField(_("ID da Moeda"), default=57)
    multiplicador = models.DecimalField(
        _("Multiplicador (ex: 2.0 para 2x)"), max_digits=5, decimal_places=2, default=1.0
    )
    ativa = models.BooleanField(_("Moeda Ativa"), default=True)

    class Meta:
        verbose_name = _("Configuração de Moeda")
        verbose_name_plural = _("Configurações de Moeda")

    def save(self, *args, **kwargs):
        if self.ativa:
            CoinConfig.objects.exclude(pk=self.pk).update(ativa=False)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.nome} - ID: {self.coin_id} - x{self.multiplicador}"
