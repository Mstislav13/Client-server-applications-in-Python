import sys
import json
import socket
import time
import argparse
import logging
import log.client_log_config
from errors import ReqDictMissFiledError
from common.variables import ACTION, PRESENCE, TIME, PORT, USER, ACCOUNT_NAME, \
    RESPONSE, ERROR, CONNECTIONS_IP_ADDRESS, CONNECTIONS_PORT
from common.utils import listen_message, send_message
from decos import log


# Инициализация клиентского логирования
CLIENT_LOGGER = logging.getLogger('client')


@log
def create_presence(account_name='Guest'):
    '''
    Функция генерирует запрос о присутствии клиента
    '''
    out = {
        ACTION: PRESENCE,
        TIME: time.time(),
        PORT: CONNECTIONS_PORT,
        USER: {
            ACCOUNT_NAME: account_name
        }
    }
    CLIENT_LOGGER.debug(f'Сформировано сообщение: {PRESENCE}, для пользователя {account_name}')
    return out


@log
def answer_server(message):
    '''
    Функция разбирает ответ сервера
    '''
    CLIENT_LOGGER.debug(f'Разбор сообщения от сервера: {message}')
    if RESPONSE in message:
        if message[RESPONSE] == 200:
            return '200 : OK'
        return f'400 : {message[ERROR]}'
    raise ReqDictMissFiledError(RESPONSE)


@log
def create_arg_parser():
    '''
    Создание парсера аргументов командной строки
    '''
    parser = argparse.ArgumentParser()
    parser.add_argument('addr', default=CONNECTIONS_IP_ADDRESS, nargs='?')
    parser.add_argument('port', default=CONNECTIONS_PORT, type=int, nargs='?')
    return parser


def main():
    '''
    Загружаем параметы коммандной строки
    '''
    parser = create_arg_parser()
    namespace = parser.parse_args(sys.argv[1:])
    addr_server = namespace.addr
    port_server = namespace.port

    # Проверяем подходящий номер порта.
    if not 1023 < port_server < 65536:
        CLIENT_LOGGER.critical(
            f'Попытка подключения клиента с неподходящим: {port_server} номером порта.'
            f'Допустимые номера портов с 1024 до 65535. Подключение завершается.'
        )
        sys.exit(1)

    CLIENT_LOGGER.info(f'Подключен клиент. Адрес сервера пользователя: {addr_server}, номер порта: {port_server}')

    # Инициализация сокета и обмен
    try:
        transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        transport.connect((addr_server, port_server))
        message_to_server = create_presence()
        send_message(transport, message_to_server)
        answer = answer_server(listen_message(transport))
        CLIENT_LOGGER.info(f'Принят ответ от сервера: {answer}')
        print(answer)
    except json.JSONDecodeError:
        CLIENT_LOGGER.error('Не удалось декодировать полученную JSON строку.')
    except ReqDictMissFiledError as missing_error:
        CLIENT_LOGGER.error(f'В ответе сервера отсутствует необходимое поле: {missing_error.missing_field}')
    except ConnectionRefusedError:
        CLIENT_LOGGER.critical(f'Не удалось подключиться к серверу {addr_server}:{port_server},'
                               f'сервер отклонил запрос на подключение.')


if __name__ == '__main__':
    main()
