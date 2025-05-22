from apps.lineage.wallet.models import Wallet, TransacaoWallet
from django.db.models import Sum


def saldo_usuario(usuario):
    try:
        wallet = Wallet.objects.get(usuario=usuario)
        saldo_wallet = wallet.saldo
    except Wallet.DoesNotExist:
        return {
            'saldo_wallet': 0,
            'saldo_calculado': 0,
            'diferenca': 0
        }

    entradas = TransacaoWallet.objects.filter(
        wallet=wallet, tipo='ENTRADA'
    ).aggregate(total=Sum('valor'))['total'] or 0

    saidas = TransacaoWallet.objects.filter(
        wallet=wallet, tipo='SAIDA'
    ).aggregate(total=Sum('valor'))['total'] or 0

    saldo_calculado = entradas - saidas

    return {
        'saldo_wallet': saldo_wallet,
        'saldo_calculado': saldo_calculado,
        'diferenca': saldo_wallet - saldo_calculado
    }
