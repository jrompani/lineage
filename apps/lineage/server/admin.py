from django.contrib import admin
from .models import *
from core.admin import BaseModelAdmin
from django.contrib import messages
from django.utils import timezone


@admin.register(ApiEndpointToggle)
class ApiEndpointToggleAdmin(BaseModelAdmin):
    list_display = [
        'players_online',
        'top_pvp',
        'top_pk',
        'top_clan',
        'top_rich',
        'top_online',
        'top_level',
        'olympiad_ranking',
        'olympiad_all_heroes',
        'olympiad_current_heroes',
        'grandboss_status',
        'raidboss_status',
        'siege',
        'siege_participants',
        'boss_jewel_locations',
    ]

    list_editable = list_display  # permite edição inline no list view
    list_display_links = None  # remove link para a edição detalhada
    actions = None  # remove ações em massa para evitar exclusões acidentais

    def has_add_permission(self, request):
        # Permite adicionar apenas se ainda não houver nenhum registro
        return not ApiEndpointToggle.objects.exists()

    def has_delete_permission(self, request, obj=None):
        # Impede a exclusão do registro
        return False


class IndexConfigTranslationInline(admin.TabularInline):
    model = IndexConfigTranslation
    extra = 1
    fields = ('language', 'nome_servidor', 'descricao_servidor', 'jogadores_online_texto')
    min_num = 1


@admin.register(IndexConfig)
class IndexConfigAdmin(BaseModelAdmin):
    list_display = (
        'nome_servidor', 'link_patch', 'link_cliente', 'link_discord', 
        'trailer_video_id', 'imagem_banner'
    )
    search_fields = ('nome_servidor',)
    list_filter = ()

    inlines = [IndexConfigTranslationInline]

    fieldsets = (
        (None, {
            'fields': ('nome_servidor', 'descricao_servidor', 'link_patch', 'link_cliente', 'link_discord')
        }),
        ('Configurações de Trailer', {
            'fields': ('trailer_video_id',)
        }),
        ('Configurações de Exibição', {
            'fields': ('jogadores_online_texto', 'imagem_banner')
        }),
    )

    def save_model(self, request, obj, form, change):
        if not change and IndexConfig.objects.exists():
            self.message_user(
                request,
                "Apenas um registro de configuração do servidor pode existir. Por favor, edite o existente.",
                messages.WARNING
            )
            return
        super().save_model(request, obj, form, change)


@admin.register(ServicePrice)
class ServicePriceAdmin(BaseModelAdmin):
    list_display = ('servico', 'preco')


@admin.register(ActiveAdenaExchangeItem)
class ActiveAdenaExchangeItemAdmin(BaseModelAdmin):
    list_display = ('item_type', 'value_item', 'active', 'created_at')
    list_filter = ('active',)
    search_fields = ('item_type',)


@admin.register(Apoiador)
class ApoiadorAdmin(BaseModelAdmin):
    list_display = ('nome_publico', 'user', 'ativo')
    search_fields = ('nome_publico', 'user__username')


@admin.register(Comissao)
class ComissaoAdmin(admin.ModelAdmin):
    # Exibir colunas no list display
    list_display = ('apoiador', 'compra', 'valor', 'pago', 'data_pagamento')
    # Filtros para facilitar a busca no admin
    list_filter = ('pago', 'apoiador', 'data_pagamento')
    # Adicionar campos de pesquisa no admin
    search_fields = ('apoiador__nome_publico', 'compra__user__username')
    # Formulários personalizados no admin
    readonly_fields = ('data_pagamento',)

    # Definir campos editáveis
    fields = ('apoiador', 'compra', 'valor', 'pago', 'data_pagamento')

    # Mostrar o campo de data de pagamento se já for pago
    def save_model(self, request, obj, form, change):
        if obj.pago and not obj.data_pagamento:
            obj.data_pagamento = timezone.now()
        super().save_model(request, obj, form, change)
