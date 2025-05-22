URL_RATE_LIMITS_DICT = {
    '/app/server/api/players-online/':             {'rate': '30/m', 'key': 'ip', 'group': 'public-api'},
    '/app/server/api/top-pvp/':                    {'rate': '30/m', 'key': 'ip', 'group': 'public-api'},
    '/app/server/api/top-pk/':                     {'rate': '30/m', 'key': 'ip', 'group': 'public-api'},
    '/app/server/api/top-clan/':                   {'rate': '30/m', 'key': 'ip', 'group': 'public-api'},
    '/app/server/api/top-rich/':                   {'rate': '30/m', 'key': 'ip', 'group': 'public-api'},
    '/app/server/api/top-online/':                 {'rate': '30/m', 'key': 'ip', 'group': 'public-api'},
    '/app/server/api/top-level/':                  {'rate': '30/m', 'key': 'ip', 'group': 'public-api'},
    '/app/server/api/olympiad-ranking/':           {'rate': '30/m', 'key': 'ip', 'group': 'public-api'},
    '/app/server/api/olympiad-heroes/':            {'rate': '30/m', 'key': 'ip', 'group': 'public-api'},
    '/app/server/api/olympiad-current-heroes/':    {'rate': '30/m', 'key': 'ip', 'group': 'public-api'},
    '/app/server/api/grandboss-status/':           {'rate': '30/m', 'key': 'ip', 'group': 'public-api'},
    '/app/server/api/siege/':                      {'rate': '30/m', 'key': 'ip', 'group': 'public-api'},
    '/app/server/api/siege-participants/':         {'rate': '30/m', 'key': 'ip', 'group': 'public-api'},
    '/app/server/api/boss-jewel-locations/':       {'rate': '30/m', 'key': 'ip', 'group': 'public-api'},

    '/app/wallet/transfer/servidor/': {'rate': '5/m', 'key': 'user_or_ip', 'group': 'wallet-transfers'},
    '/app/wallet/transfer/jogador/':  {'rate': '5/m', 'key': 'user_or_ip', 'group': 'wallet-transfers'},
}
