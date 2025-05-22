from datetime import datetime, timedelta
import time

# O timestamp que você forneceu (1746182022) já está em segundos
respawn_timestamp = 1746182022  # Substitua com o valor do respawn do banco
gmt_offset = -3  # Fuso horário, por exemplo UTC-3

# Calcular o tempo de respawn
current_time = time.time()  # Tempo atual em segundos
if respawn_timestamp > current_time:
    respawn_datetime = datetime.fromtimestamp(respawn_timestamp) - timedelta(hours=gmt_offset)
    respawn_human = respawn_datetime.strftime('%d/%m/%Y %H:%M')
    status = "Ativo"
else:
    respawn_human = '-'
    status = "Inativo"

print(f"Status: {status}")
print(f"Respawn: {respawn_human}")
