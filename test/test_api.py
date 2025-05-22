import requests
import time
import random

# URL_RATE_LIMITS_DICT fornecido
URL_RATE_LIMITS_DICT = {
    '/app/server/api/players-online/': {'rate': '30/m', 'key': 'ip', 'group': 'public-api'},
    '/app/server/api/top-pvp/': {'rate': '30/m', 'key': 'ip', 'group': 'public-api'},
    '/app/server/api/top-pk/': {'rate': '30/m', 'key': 'ip', 'group': 'public-api'},
    '/app/server/api/top-clan/': {'rate': '30/m', 'key': 'ip', 'group': 'public-api'},
    '/app/server/api/top-rich/': {'rate': '30/m', 'key': 'ip', 'group': 'public-api'},
    '/app/server/api/top-online/': {'rate': '30/m', 'key': 'ip', 'group': 'public-api'},
    '/app/server/api/top-level/': {'rate': '30/m', 'key': 'ip', 'group': 'public-api'},
    '/app/server/api/olympiad-ranking/': {'rate': '30/m', 'key': 'ip', 'group': 'public-api'},
    '/app/server/api/olympiad-heroes/': {'rate': '30/m', 'key': 'ip', 'group': 'public-api'},
    '/app/server/api/olympiad-current-heroes/': {'rate': '30/m', 'key': 'ip', 'group': 'public-api'},
    '/app/server/api/grandboss-status/': {'rate': '30/m', 'key': 'ip', 'group': 'public-api'},
    '/app/server/api/siege/': {'rate': '30/m', 'key': 'ip', 'group': 'public-api'},
    '/app/server/api/siege-participants/': {'rate': '30/m', 'key': 'ip', 'group': 'public-api'},  # com path param
    '/app/server/api/boss-jewel-locations/': {'rate': '30/m', 'key': 'ip', 'group': 'public-api'},
}

BASE_URL = 'http://127.0.0.1'  # Troque pelo seu endereço base

# Função para testar cada endpoint com parâmetros dinâmicos
def test_endpoint(endpoint, params=None):
    url = BASE_URL + endpoint
    
    # Tratamento específico para o endpoint 'siege-participants'
    if "siege-participants" in endpoint and params and 'castle_id' in params:
        url = BASE_URL + f"/app/server/api/siege-participants/{params['castle_id']}/"
    
    # Tratamento específico para o endpoint 'boss-jewel-locations'
    if "boss-jewel-locations" in endpoint and params and 'ids' in params:
        url = BASE_URL + f"/app/server/api/boss-jewel-locations/?ids={params['ids']}"

    print(f'Testando {url}...')
    
    try:
        response = requests.get(url)

        if response.status_code == 200:
            print(f'Success: {endpoint} -> {response.status_code}')
        else:
            print(f'Failed: {endpoint} -> {response.status_code} - {response.text}')
            if response.status_code == 404:
                print(f"Detalhes: Endpoint não encontrado. Verifique a URL ou a lógica da view.")
            elif response.status_code == 500:
                print(f"Detalhes: Erro no servidor. Tente novamente mais tarde.")
    except requests.exceptions.RequestException as e:
        print(f"Erro na requisição: {e}")

# Função para gerar parâmetros aleatórios
def get_random_params(endpoint):
    if "siege-participants" in endpoint:
        # Randomizando o castle_id entre 1 e 9
        return {'castle_id': random.randint(1, 9)}
    
    if "boss-jewel-locations" in endpoint:
        # IDs permitidos para boss jewel locations
        allowed_ids = [6656, 6657, 6658, 6659, 6660, 6661, 8191]
        # Randomizando os IDs
        random_ids = random.sample(allowed_ids, k=random.randint(1, len(allowed_ids)))  # seleciona entre 1 e todos os IDs
        return {'ids': ','.join(map(str, random_ids))}
    
    # Para outros endpoints sem parâmetros dinâmicos
    return None

# Testar todos os endpoints
def test_all_endpoints():
    for endpoint, config in URL_RATE_LIMITS_DICT.items():
        params = get_random_params(endpoint)
        test_endpoint(endpoint, params)
        time.sleep(2)  # Espera entre as requisições para evitar rate limit

# Rodando os testes
if __name__ == "__main__":
    test_all_endpoints()
