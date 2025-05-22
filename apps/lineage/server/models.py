from django.db import models
from django.core.exceptions import ValidationError
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from core.models import BaseModel
from apps.main.home.models import User
from apps.lineage.shop.models import ShopPurchase
import os
import uuid


def caminho_imagem_apoiador(instance, filename):
    nome_base, extensao = os.path.splitext(filename)
    novo_nome = f"{slugify(instance.nome_publico)}-{uuid.uuid4().hex[:8]}{extensao}"
    return os.path.join("apoiadores", novo_nome[:95])


class ApiEndpointToggle(BaseModel):
    players_online = models.BooleanField(default=True, verbose_name=_("Players Online"))
    top_pvp = models.BooleanField(default=True, verbose_name=_("Top PvP"))
    top_pk = models.BooleanField(default=True, verbose_name=_("Top PK"))
    top_clan = models.BooleanField(default=True, verbose_name=_("Top Clan"))
    top_rich = models.BooleanField(default=True, verbose_name=_("Top Rich"))
    top_online = models.BooleanField(default=True, verbose_name=_("Top Online"))
    top_level = models.BooleanField(default=True, verbose_name=_("Top Level"))
    olympiad_ranking = models.BooleanField(default=True, verbose_name=_("Olympiad Ranking"))
    olympiad_all_heroes = models.BooleanField(default=True, verbose_name=_("Olympiad All Heroes"))
    olympiad_current_heroes = models.BooleanField(default=True, verbose_name=_("Olympiad Current Heroes"))
    grandboss_status = models.BooleanField(default=True, verbose_name=_("Grand Boss Status"))
    raidboss_status = models.BooleanField(default=True, verbose_name=_("Raid Boss Status"))
    siege = models.BooleanField(default=True, verbose_name=_("Siege"))
    siege_participants = models.BooleanField(default=True, verbose_name=_("Siege Participants"))
    boss_jewel_locations = models.BooleanField(default=True, verbose_name=_("Boss Jewel Locations"))

    class Meta:
        verbose_name = _("API Endpoint Toggle")
        verbose_name_plural = _("API Endpoint Toggles")

    def __str__(self):
        return _("API Endpoint Configuration")


class IndexConfig(BaseModel):
    nome_servidor = models.CharField(max_length=100, default="Lineage 2 PDL", verbose_name=_("Server Name"))
    descricao_servidor = models.CharField(max_length=255, blank=True, default=_("Onde Lendas Nascem, Heróis Lutam e a Glória É Eterna."), verbose_name=_("Server Description"))
    link_patch = models.URLField(default="https://pdl.denky.dev.br/", verbose_name=_("Patch Link"))
    link_cliente = models.URLField(default="https://pdl.denky.dev.br/", verbose_name=_("Client Link"))
    link_discord = models.URLField(default="https://pdl.denky.dev.br/", verbose_name=_("Discord Link"))
    trailer_video_id = models.CharField(max_length=100, blank=True, default="CsNutvmrHIA?si=2lF1z1jPFkf8uGJB", verbose_name=_("Trailer Video ID"))
    jogadores_online_texto = models.CharField(max_length=255, blank=True, default=_("jogadores online Agora"), verbose_name=_("Players Online Text"))
    imagem_banner = models.ImageField(upload_to='banners/', blank=True, null=True, verbose_name=_("Banner Image"))

    class Meta:
        verbose_name = _("Index Configuration")
        verbose_name_plural = _("Index Configuration")

    def save(self, *args, **kwargs):
        if not self.pk and IndexConfig.objects.exists():
            raise ValidationError(_("Only one server configuration is allowed."))
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nome_servidor


class IndexConfigTranslation(BaseModel):
    LANGUAGES = [
        ('pt', _('Português')),
        ('en', _('English')),
        ('es', _('Español')),
    ]

    config = models.ForeignKey(IndexConfig, on_delete=models.CASCADE, related_name='translations', verbose_name=_("Configuration"))
    language = models.CharField(max_length=5, choices=LANGUAGES, verbose_name=_("Language"))
    nome_servidor = models.CharField(max_length=100, verbose_name=_("Server Name"))
    descricao_servidor = models.CharField(max_length=255, blank=True, verbose_name=_("Server Description"))
    jogadores_online_texto = models.CharField(max_length=255, blank=True, verbose_name=_("Players Online Text"))

    class Meta:
        unique_together = ('config', 'language')
        verbose_name = _("Index Configuration Translation")
        verbose_name_plural = _("Index Configuration Translations")

    def __str__(self):
        return f"{self.nome_servidor} ({self.language})"


class ServicePrice(BaseModel):
    SERVICO_CHOICES = [
        ('CHANGE_NICKNAME', _('Change Nickname')),
        ('CHANGE_SEX', _('Change Gender')),
    ]

    servico = models.CharField(max_length=30, choices=SERVICO_CHOICES, unique=True, verbose_name=_("Service"))
    preco = models.DecimalField(max_digits=10, decimal_places=2, default=10.00, verbose_name=_("Price"))

    def __str__(self):
        return f"{self.get_servico_display()} - R${self.preco}"

    @classmethod
    def create_default(cls):
        if not cls.objects.exists():
            cls.objects.create(servico='CHANGE_NICKNAME', preco=10.00)
            cls.objects.create(servico='CHANGE_SEX', preco=10.00)

    class Meta:
        verbose_name = _("Service Price")
        verbose_name_plural = _("Service Prices")


class ActiveAdenaExchangeItem(BaseModel):
    item_type = models.PositiveIntegerField(verbose_name=_("Item ID"), help_text=_("ID of the item used for Adena exchange"))
    value_item = models.PositiveIntegerField(default=1_000_000, verbose_name=_("Adena Value"), help_text=_("Amount of Adena each item represents"))
    active = models.BooleanField(default=False, verbose_name=_("Active"), help_text=_("Mark as active to be used in calculation"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))

    class Meta:
        verbose_name = _("Active Adena Exchange Item")
        verbose_name_plural = _("Active Adena Exchange Items")

    def __str__(self):
        status = _("Active") if self.active else _("Inactive")
        return f"{_('Item')} {self.item_type} - {status}"


class Apoiador(BaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name=_("User"))
    nome_publico = models.CharField(max_length=100, verbose_name=_("Public Name"))
    descricao = models.TextField(blank=True, verbose_name=_("Description"))
    link_twitch = models.URLField(blank=True, verbose_name=_("Twitch Link"))
    link_youtube = models.URLField(blank=True, verbose_name=_("YouTube Link"))
    imagem = models.ImageField(upload_to=caminho_imagem_apoiador, null=True, blank=True, verbose_name=_("Image"))
    ativo = models.BooleanField(default=True, verbose_name=_("Active"))

    STATUS_CHOICES = [
        ('pendente', _('Pending')),
        ('aprovado', _('Approved')),
        ('rejeitado', _('Rejected')),
        ('expirado', _('Expired')),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pendente', verbose_name=_("Status"))

    class Meta:
        verbose_name = _("Supporter")
        verbose_name_plural = _("Supporters")

    def __str__(self):
        return self.nome_publico


class Comissao(BaseModel):
    apoiador = models.ForeignKey(Apoiador, on_delete=models.CASCADE, verbose_name=_("Supporter"))
    compra = models.ForeignKey(ShopPurchase, on_delete=models.CASCADE, verbose_name=_("Shop Purchase"))
    valor = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_("Value"))
    data_pagamento = models.DateTimeField(auto_now_add=True, verbose_name=_("Payment Date"))
    pago = models.BooleanField(default=False, verbose_name=_("Paid"))

    class Meta:
        verbose_name = _("Commission")
        verbose_name_plural = _("Commissions")

    def __str__(self):
        return f"{_('Commission from')} {self.apoiador.nome_publico} - R${self.valor}"
