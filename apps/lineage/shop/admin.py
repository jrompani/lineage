from django.contrib import admin
from core.admin import BaseModelAdmin
from .models import *


@admin.register(ShopItem)
class ShopItemAdmin(BaseModelAdmin):
    list_display = ('nome', 'item_id', 'quantidade', 'preco', 'ativo')
    list_filter = ('ativo',)
    search_fields = ('nome', 'item_id')
    ordering = ('nome',)


@admin.register(ShopPackage)
class ShopPackageAdmin(BaseModelAdmin):
    list_display = ('nome', 'preco_total', 'ativo', 'promocao')
    list_filter = ('ativo', 'promocao')
    search_fields = ('nome',)
    ordering = ('nome',)


@admin.register(PromotionCode)
class PromotionCodeAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'desconto_percentual', 'ativo', 'validade', 'apoiador')
    search_fields = ('codigo',)
    list_filter = ('ativo',)


@admin.register(Cart)
class CartAdmin(BaseModelAdmin):
    list_display = ('user', 'promocao_aplicada', 'calcular_total')
    search_fields = ('user__username',)
    ordering = ('user',)


@admin.register(ShopPurchase)
class ShopPurchaseAdmin(BaseModelAdmin):
    list_display = ('user', 'character_name', 'total_pago', 'data_compra', 'promocao_aplicada')
    list_filter = ('data_compra',)
    search_fields = ('user__username', 'character_name')
    ordering = ('-data_compra',)


@admin.register(ShopPackageItem)
class ShopPackageItemAdmin(BaseModelAdmin):
    list_display = ('pacote', 'item', 'quantidade')
    search_fields = ('pacote__nome', 'item__nome')
    ordering = ('pacote', 'item')


@admin.register(CartItem)
class CartItemAdmin(BaseModelAdmin):
    list_display = ('cart', 'item', 'quantidade')
    search_fields = ('cart__user__username', 'item__nome')
    ordering = ('cart',)


@admin.register(CartPackage)
class CartPackageAdmin(BaseModelAdmin):
    list_display = ('cart', 'pacote', 'quantidade')
    search_fields = ('cart__user__username', 'pacote__nome')
    ordering = ('cart',)
