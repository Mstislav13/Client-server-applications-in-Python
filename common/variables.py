"""Константы"""

# Порт поумолчанию для сетевого ваимодействия
CONNECTIONS_PORT = 7777
# IP адрес по умолчанию для подключения клиента
CONNECTIONS_IP_ADDRESS = '127.0.0.1'
# Максимальная очередь подключений
MAX_TURN_CONNECTIONS = 5
# Максимальная длинна сообщения в байтах
MAX_LENGTH_MESSAGE = 1024
# Кодировка проекта
PROJECT_ENCODING = 'utf-8'

# Прококол JIM основные ключи:
ACTION = 'action'
TIME = 'time'
USER = 'user'
ACCOUNT_NAME = 'account_name'
PORT = 'port'

# Прочие ключи, используемые в протоколе
PRESENCE = 'presence'
RESPONSE = 'response'
ERROR = 'error'
RESPONDEFAULT_IP_ADDRESSSE = 'respondefault_ip_addressse'
