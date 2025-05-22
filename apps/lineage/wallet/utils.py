from django.db import transaction
from .models import *
from .signals import aplicar_transacao
from django.utils.translation import gettext as _


def transferir_para_jogador(wallet_origem, wallet_destino, valor, descricao="Transferência entre jogadores"):

    if wallet_origem.saldo < valor:
        raise ValueError(_("Saldo insuficiente para transferência."))

    with transaction.atomic():
        # Debita da carteira de origem
        aplicar_transacao(
            wallet=wallet_origem,
            tipo="SAIDA",
            valor=valor,
            descricao=descricao,
            origem=wallet_origem.usuario.username,
            destino=wallet_destino.usuario.username
        )

        # Credita na carteira de destino
        aplicar_transacao(
            wallet=wallet_destino,
            tipo="ENTRADA",
            valor=valor,
            descricao=descricao,
            origem=wallet_origem.usuario.username,
            destino=wallet_destino.usuario.username
        )
