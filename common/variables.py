import logging

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
# Текущий уровень логирования
LOGGING_LEVEL = logging.DEBUG

# Прококол JIM основные ключи:
ACTION = 'action'
TIME = 'time'
USER = 'user'
ACCOUNT_NAME = 'account_name'
PORT = 'port'
SENDER = 'sender'
WHITHER = 'to'

# Прочие ключи, используемые в протоколе
PRESENCE = 'presence'
RESPONSE = 'response'
ERROR = 'error'
RESPONDEFAULT_IP_ADDRESSSE = 'respondefault_ip_addressse'
MESSAGE = 'message'
MESSAGE_TEXT = 'message_text'
EXIT = 'exit'

# Словари - ответы:
RESPONSE_200 = {RESPONSE: 200}
RESPONSE_400 = {
    RESPONSE: 400,
    ERROR: None
}
