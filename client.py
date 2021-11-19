import sys
import json
import socket
import time
import argparse
import logging
import log.client_log_config
from errors import RecivedIncorrectDataError, ReqDictMissFiledError, ServerError
from common.variables import ACTION, PRESENCE, TIME, USER, ACCOUNT_NAME, \
    RESPONSE, ERROR, CONNECTIONS_IP_ADDRESS, CONNECTIONS_PORT, SENDER, MESSAGE, MESSAGE_TEXT, WHITHER, EXIT
from common.utils import listen_message, send_message
from decos import log
import threading

# Инициализация клиентского логирования
CLIENT_LOGGER = logging.getLogger('client')


@log
def create_presence(_socket, account_name):
    while True:
        wither = input('Кому отправить: ')
        text = input('Текст сообщения: ')
        scroll_dict = {
            ACTION: MESSAGE,
            SENDER: account_name,
            WHITHER: wither,
            TIME: time.time(),
            MESSAGE_TEXT: text
        }
        CLIENT_LOGGER.debug(f'Сформирован словарь сообщения: {scroll_dict}')
        try:
            send_message(_socket, scroll_dict)
            CLIENT_LOGGER.info(f'Клиенту: {wither} отправлено сообщение.')
        except:
            CLIENT_LOGGER.critical(f'Потеряно соединение.')
            sys.exit(1)


@log
def answer_clients(_socket, clients):
    while True:
        try:
            missive = listen_message(_socket)
            if ACTION in missive and missive[ACTION] == MESSAGE and SENDER in missive and WHITHER in missive and \
                    MESSAGE_TEXT in missive and missive[WHITHER] == clients:
                print(f'\nПолучено сообщение от пользователя: {missive[SENDER]}:\n{missive[MESSAGE_TEXT]}')
                CLIENT_LOGGER.info(f'Получено сообщение от пользователя: {missive[SENDER]}: {missive[MESSAGE_TEXT]}')
            else:
                CLIENT_LOGGER.error(f'Получено некорректное сообщение с сервера: {missive}')
        except RecivedIncorrectDataError:
            CLIENT_LOGGER.error(f'Не удалось декодировать полученное сообщение.')
        except (OSError, ConnectionError, ConnectionAbortedError, ConnectionResetError, json.JSONDecodeError):
            CLIENT_LOGGER.critical(f'Потеряно соединение с сервером.')
            break


@log
def create_answer(account_name):
    """Запрос о нахождении клиента в сети"""
    out = {
        ACTION: PRESENCE,
        TIME: time.time(),
        USER: {
            ACCOUNT_NAME: account_name
        }
    }
    CLIENT_LOGGER.debug(f'Сформировано {PRESENCE} сообщение для пользователя {account_name}')
    return out


# @log
# def if_exit(account_name):
#     return {
#         ACTION: EXIT,
#         TIME: time.time(),
#         ACCOUNT_NAME: account_name
#     }


@log
def process_response_answer(missive):
    CLIENT_LOGGER.debug(f'Серверное сообщение: {missive}')
    if RESPONSE in missive:
        if missive[RESPONSE] == 200:
            return '200 : LUCK'
        elif missive[RESPONSE] == 400:
            raise ServerError(f'400 : {missive[ERROR]}')
    raise ReqDictMissFiledError(RESPONSE)


@log
def create_arg_parser():
    '''
    Создание парсера аргументов командной строки
    '''
    compare = argparse.ArgumentParser()
    compare.add_argument('addr', default=CONNECTIONS_IP_ADDRESS, nargs='?')
    compare.add_argument('port', default=CONNECTIONS_PORT, type=int, nargs='?')
    compare.add_argument('-n', '--name', default=None, nargs='?')
    namespace = compare.parse_args(sys.argv[1:])
    addr_server = namespace.addr
    port_server = namespace.port
    client_name = namespace.name

    if port_server == (range(1024, 65536)):
        CLIENT_LOGGER.critical(
            f'Попытка подключения клиента с неподходящим: {port_server} номером порта.'
            f'Допустимые номера портов с 1024 до 65535. Подключение завершается.'
        )
        sys.exit(1)

    return addr_server, port_server, client_name


def main():
    '''
    Загружаем параметы коммандной строки
    '''
    addr_server, port_server, client_name = create_arg_parser()
    print(f'Месинджер клиента: {client_name}.')

    if not client_name:
        client_name = input('Введите имя пользователя: ')

    CLIENT_LOGGER.info(f'Подключен клиент. Адрес сервера пользователя: {addr_server}, номер порта: {port_server}, '
                       f'имя пользователя: {client_name}')

    try:
        transmit = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        transmit.connect((addr_server, port_server))
        send_message(transmit, create_answer(client_name))
        answer = process_response_answer(listen_message(transmit))
        CLIENT_LOGGER.info(f'Принят ответ от сервера: {answer}')
        print(f'Установлено соединение с сервером.')
    except json.JSONDecodeError:
        CLIENT_LOGGER.error('Не удалось декодировать полученную JSON строку.')
        sys.exit(1)
    except ServerError as error:
        CLIENT_LOGGER.error(f'При установке соединения сервер вернул ошибку: {error.text}')
        sys.exit(1)
    except ReqDictMissFiledError as missing_error:
        CLIENT_LOGGER.error(f'В ответе сервера отсутствует необходимое поле: {missing_error.missing_field}')
        sys.exit(1)
    except (ConnectionRefusedError, ConnectionError):
        CLIENT_LOGGER.critical(f'Не удалось подключиться к серверу {addr_server}:{port_server},'
                               f'сервер отклонил запрос на подключение.')
        sys.exit(1)
    else:
        recipient = threading.Thread(target=answer_clients, args=(transmit, client_name))
        recipient.daemon = True
        recipient.start()

        meeting_room = threading.Thread(target=create_presence, args=(transmit, client_name))
        meeting_room.daemon = True
        meeting_room.start()
        CLIENT_LOGGER.debug('Начались переговоры.')

        while True:
            time.sleep(1)
            if recipient.is_alive() and meeting_room.is_alive():
                continue
            break


if __name__ == '__main__':
    main()
