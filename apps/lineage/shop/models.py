from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from apps.main.home.models import User
from core.models import BaseModel


class ShopItem(BaseModel):
    nome = models.CharField(_("Nome"), max_length=100)
    item_id = models.PositiveIntegerField(_("ID do Item"))
    preco = models.DecimalField(_("Preço"), max_digits=10, decimal_places=2)
    quantidade = models.PositiveIntegerField(_("Quantidade"), default=1)
    ativo = models.BooleanField(_("Ativo"), default=True)

    class Meta:
        verbose_name = _("Item da Loja")
        verbose_name_plural = _("Itens da Loja")

    def __str__(self):
        return f"{self.nome} ({self.quantidade}x) — R${self.preco}"


class PromotionCode(BaseModel):
    codigo = models.CharField(_("Código"), max_length=50, unique=True)
    desconto_percentual = models.DecimalField(_("Desconto Percentual"), max_digits=5, decimal_places=2)
    ativo = models.BooleanField(_("Ativo"), default=True)
    validade = models.DateTimeField(_("Validade"), null=True, blank=True)
    apoiador = models.ForeignKey(
        'server.Apoiador', verbose_name=_("Apoiador"), null=True, blank=True, on_delete=models.SET_NULL
    )

    class Meta:
        verbose_name = _("Código Promocional")
        verbose_name_plural = _("Códigos Promocionais")

    def is_valido(self):
        if not self.ativo:
            return False
        if self.validade and timezone.now() > self.validade:
            return False
        return True

    def __str__(self):
        return f"{self.codigo} — {self.desconto_percentual}%"


class ShopPackage(BaseModel):
    nome = models.CharField(_("Nome"), max_length=100)
    preco_total = models.DecimalField(_("Preço Total"), max_digits=10, decimal_places=2)
    itens = models.ManyToManyField(ShopItem, through='ShopPackageItem', verbose_name=_("Itens"))
    ativo = models.BooleanField(_("Ativo"), default=True)
    promocao = models.ForeignKey(
        PromotionCode, verbose_name=_("Promoção"), null=True, blank=True, on_delete=models.SET_NULL
    )

    class Meta:
        verbose_name = _("Pacote da Loja")
        verbose_name_plural = _("Pacotes da Loja")

    def __str__(self):
        return f"{self.nome} — R${self.preco_total}"


class ShopPackageItem(BaseModel):
    pacote = models.ForeignKey(ShopPackage, verbose_name=_("Pacote"), on_delete=models.CASCADE)
    item = models.ForeignKey(ShopItem, verbose_name=_("Item"), on_delete=models.CASCADE)
    quantidade = models.PositiveIntegerField(_("Quantidade"), default=1)

    class Meta:
        verbose_name = _("Item do Pacote")
        verbose_name_plural = _("Itens do Pacote")

    def __str__(self):
        return f"{self.pacote.nome} — {self.item.nome} x{self.quantidade}"


class Cart(BaseModel):
    user = models.OneToOneField(User, verbose_name=_("Usuário"), on_delete=models.CASCADE, related_name='cart')
    itens = models.ManyToManyField(ShopItem, through='CartItem', verbose_name=_("Itens"))
    pacotes = models.ManyToManyField(ShopPackage, through='CartPackage', verbose_name=_("Pacotes"))
    promocao_aplicada = models.ForeignKey(
        PromotionCode, verbose_name=_("Promoção Aplicada"), null=True, blank=True, on_delete=models.SET_NULL
    )

    class Meta:
        verbose_name = _("Carrinho")
        verbose_name_plural = _("Carrinhos")

    def calcular_total(self):
        total = sum(ci.item.preco * ci.quantidade for ci in self.cartitem_set.all())
        total += sum(cp.pacote.preco_total * cp.quantidade for cp in self.cartpackage_set.all())
        if self.promocao_aplicada and self.promocao_aplicada.is_valido():
            total *= (1 - (self.promocao_aplicada.desconto_percentual / 100))
        return total

    def limpar(self):
        self.itens.clear()
        self.pacotes.clear()
        self.promocao_aplicada = None
        self.save()

    def __str__(self):
        return f"Carrinho de {self.user.username}"


class CartItem(BaseModel):
    cart = models.ForeignKey(Cart, verbose_name=_("Carrinho"), on_delete=models.CASCADE)
    item = models.ForeignKey(ShopItem, verbose_name=_("Item"), on_delete=models.CASCADE)
    quantidade = models.PositiveIntegerField(_("Quantidade"), default=1)

    class Meta:
        verbose_name = _("Item no Carrinho")
        verbose_name_plural = _("Itens no Carrinho")

    def __str__(self):
        return f"{self.quantidade}x {self.item.nome} (Carrinho de {self.cart.user.username})"


class CartPackage(BaseModel):
    cart = models.ForeignKey(Cart, verbose_name=_("Carrinho"), on_delete=models.CASCADE)
    pacote = models.ForeignKey(ShopPackage, verbose_name=_("Pacote"), on_delete=models.CASCADE)
    quantidade = models.PositiveIntegerField(_("Quantidade"), default=1)

    class Meta:
        verbose_name = _("Pacote no Carrinho")
        verbose_name_plural = _("Pacotes no Carrinho")

    def __str__(self):
        return f"{self.quantidade}x {self.pacote.nome} (Carrinho de {self.cart.user.username})"


class ShopPurchase(BaseModel):
    user = models.ForeignKey(User, verbose_name=_("Usuário"), on_delete=models.CASCADE)
    character_name = models.CharField(_("Nome do Personagem"), max_length=100)
    total_pago = models.DecimalField(_("Total Pago"), max_digits=10, decimal_places=2)
    promocao_aplicada = models.ForeignKey(
        PromotionCode, verbose_name=_("Promoção Aplicada"), null=True, blank=True, on_delete=models.SET_NULL
    )
    apoiador = models.ForeignKey(
        'server.Apoiador', verbose_name=_("Apoiador"), null=True, blank=True, on_delete=models.SET_NULL
    )
    data_compra = models.DateTimeField(_("Data da Compra"), auto_now_add=True)

    class Meta:
        verbose_name = _("Compra")
        verbose_name_plural = _("Compras")

    def save(self, *args, **kwargs):
        if self.promocao_aplicada and self.promocao_aplicada.apoiador:
            self.apoiador = self.promocao_aplicada.apoiador
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Compra de {self.user.username} — R${self.total_pago} — {self.data_compra.strftime('%d/%m/%Y %H:%M')}"
