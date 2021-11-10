import sys
import json
import socket
import time
import argparse
import logging
import log.client_log_config
from errors import ReqDictMissFiledError, ServerError
from common.variables import ACTION, PRESENCE, TIME, USER, ACCOUNT_NAME, \
    RESPONSE, ERROR, CONNECTIONS_IP_ADDRESS, CONNECTIONS_PORT, SENDER, MESSAGE, MESSAGE_TEXT
from common.utils import listen_message, send_message
from decos import log

# Инициализация клиентского логирования
CLIENT_LOGGER = logging.getLogger('client')


@log
def create_presence(sock_et, account_name='Guest'):
    '''
    Функция запрашивает текст сообщения и возвращает его
    '''
    scroll = input('Введите сообщение или \"!+!\" для выхода: ')
    if scroll == '!+!':
        sock_et.close()
        CLIENT_LOGGER.info('Выход по команде пользователя.')
        sys.exit(0)
    else:
        scroll_dict = {
            ACTION: MESSAGE,
            TIME: time.time(),
            ACCOUNT_NAME: account_name,
            MESSAGE_TEXT: scroll
        }
        CLIENT_LOGGER.debug(f'Сформирован словарь сообщения: {scroll_dict}')
    return scroll_dict


@log
def answer_server(missive):
    if ACTION in missive and missive[ACTION] == MESSAGE and SENDER in missive and MESSAGE_TEXT in missive:
        print(f'Получено сообщение от пользователя: {missive[SENDER]}:\n{missive[MESSAGE_TEXT]}')
        CLIENT_LOGGER.info(f'Получено сообщение от пользователя: {missive[SENDER]}: {missive[MESSAGE_TEXT]}')
    else:
        CLIENT_LOGGER.error(f'Получено некорректное сообщение с сервера: {missive}')


@log
def create_answer_guest(account_name='Guest'):
    out = {
        ACTION: PRESENCE,
        TIME: time.time(),
        USER: {ACCOUNT_NAME: account_name}
    }
    CLIENT_LOGGER.debug(f'Сформировано {PRESENCE} сообщение для пользователя {account_name}')
    return out


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
    compare.add_argument('-m', '--mode', default='communication', nargs='?')
    area_name = compare.parse_args(sys.argv[1:])
    addr_server = area_name.addr
    port_server = area_name.port
    client_mode = area_name.mode

    if port_server == (range(1024, 65536)):
        CLIENT_LOGGER.critical(
            f'Попытка подключения клиента с неподходящим: {port_server} номером порта.'
            f'Допустимые номера портов с 1024 до 65535. Подключение завершается.'
        )
        sys.exit(1)

    if client_mode != 'communication':
        CLIENT_LOGGER.critical(f'Недопустимый режим работы: {client_mode}, допустимый режим: communication')
        sys.exit(1)

    return addr_server, port_server, client_mode


def main():
    '''
    Загружаем параметы коммандной строки
    '''
    addr_server, port_server, client_mode = create_arg_parser()

    CLIENT_LOGGER.info(f'Подключен клиент. Адрес сервера пользователя: {addr_server}, номер порта: {port_server}, '
                       f'режим работы: {client_mode}')

    # Инициализация сокета и сообщение серверу
    try:
        transmit = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        transmit.connect((addr_server, port_server))
        send_message(transmit, create_answer_guest())
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
    except ConnectionRefusedError:
        CLIENT_LOGGER.critical(f'Не удалось подключиться к серверу {addr_server}:{port_server},'
                               f'сервер отклонил запрос на подключение.')
        sys.exit(1)
    else:
        if client_mode == 'communication':
            print('Отправка и Приём сообщений')

        while True:
            if client_mode == 'communication':  # запускаем клиента (клиент с слушатель и писатель)
                while True:
                    try:
                        send_message(transmit, create_presence(transmit))   # или клиент отправляет сообщение
                    except (ConnectionResetError, ConnectionError, ConnectionAbortedError):
                        CLIENT_LOGGER.error(f'Соединение с сервером {addr_server} было потеряно.')
                        sys.exit(1)
                    else:
                        answer_server(listen_message(transmit))   # или клиент получает сообщение


if __name__ == '__main__':
    main()
