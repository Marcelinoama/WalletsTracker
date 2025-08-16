import os
from dotenv import load_dotenv

# Carrega variáveis de ambiente do arquivo .env
load_dotenv()

# Token do bot do Telegram (obter do @BotFather)
BOT_TOKEN = os.getenv('BOT_TOKEN')

# ID do grupo onde o bot vai MONITORAR (escutar) as compras
GRUPO_MONITORAMENTO = os.getenv('GRUPO_MONITORAMENTO')  # Deixe vazio para monitorar todos os grupos

# ID do grupo onde o bot vai NOTIFICAR (enviar alertas)
GRUPO_NOTIFICACAO = os.getenv('GRUPO_NOTIFICACAO')  # Se vazio, notifica no mesmo grupo que monitora

# Quantidade mínima de compras para notificar (padrão: 10)
THRESHOLD_COMPRAS = int(os.getenv('THRESHOLD_COMPRAS', '10'))

# Tempo em segundos para resetar o contador (padrão: 1 hora = 3600 segundos)
TEMPO_RESET = int(os.getenv('TEMPO_RESET', '3600'))

# Tempo em segundos entre compras do mesmo contrato (padrão: 30 segundos)
COOLDOWN_COMPRAS = int(os.getenv('COOLDOWN_COMPRAS', '30'))

# ID dos administradores que podem configurar o bot
ADMIN_IDS = [int(x) for x in os.getenv('ADMIN_IDS', '').split(',') if x.strip()]

# Configurações de log
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
