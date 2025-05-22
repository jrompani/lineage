from django.contrib import admin
from .models import Wallet, TransacaoWallet, CoinConfig
from core.admin import BaseModelAdmin


@admin.register(Wallet)
class WalletAdmin(BaseModelAdmin):
    list_display = ['usuario', 'saldo']


@admin.register(TransacaoWallet)
class TransacaoWalletAdmin(BaseModelAdmin):
    list_display = ['wallet', 'tipo', 'valor', 'descricao', 'data']
    list_filter = ['tipo', 'data']


@admin.register(CoinConfig)
class CoinConfigAdmin(BaseModelAdmin):
    list_display = ('nome', 'coin_id', 'multiplicador', 'ativa')
    list_filter = ('ativa',)
