from apps.lineage.wallet.models import Wallet, TransacaoWallet
from django.db.models import Sum


def reconciliacao_wallet_transacoes():
    wallets = Wallet.objects.all()
    relatorio = []

    for wallet in wallets:
        total_entradas = TransacaoWallet.objects.filter(wallet=wallet, tipo='ENTRADA').aggregate(total=Sum('valor'))['total'] or 0
        total_saidas = TransacaoWallet.objects.filter(wallet=wallet, tipo='SAIDA').aggregate(total=Sum('valor'))['total'] or 0

        saldo_calculado = total_entradas - total_saidas
        diferenca = wallet.saldo - saldo_calculado

        relatorio.append({
            'usuario': wallet.usuario.username,
            'saldo_wallet': wallet.saldo,
            'entradas': total_entradas,
            'saidas': total_saidas,
            'saldo_calculado': saldo_calculado,
            'diferenca': diferenca
        })

    return relatorio
