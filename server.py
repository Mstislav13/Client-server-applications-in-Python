import socket
import sys
import json
import argparse
import logging
import time
import log.server_log_config
from errors import *
from common.variables import ACTION, ACCOUNT_NAME, RESPONSE, MAX_TURN_CONNECTIONS, \
    PRESENCE, TIME, USER, ERROR, CONNECTIONS_PORT, RESPONDEFAULT_IP_ADDRESSSE, MESSAGE, MESSAGE_TEXT, SENDER
from common.utils import listen_message, send_message
from decos import log
import select

# Инициализация логирования сервера
SERVER_LOGGER = logging.getLogger('server')


@log
def process_client_message(message, list_message, subscriber):
    '''
    Обработчик сообщений от клиентов, принимает словарь -
    сообщение от клинта, проверяет корректность,
    возвращает словарь-ответ для клиента
    '''
    SERVER_LOGGER.debug(f'Обработка сообщения от клиента: {message}')
    if ACTION in message and message[ACTION] == PRESENCE and TIME in message \
            and USER in message and message[USER][ACCOUNT_NAME] == 'Guest':
        send_message(subscriber, {RESPONSE: 200})
        return
    elif ACTION in message and message[ACTION] == MESSAGE and TIME in message and MESSAGE_TEXT in message:
        list_message.append((message[ACCOUNT_NAME], message[MESSAGE_TEXT]))
        return
    else:
        send_message(subscriber, {
            RESPONDEFAULT_IP_ADDRESSSE: 400,
            ERROR: 'Bad Request'
        })
        return


@log
def create_arg_parser():
    '''
    Создание парсера аргументов командной строки
    '''
    compare = argparse.ArgumentParser()
    compare.add_argument('-p', default=CONNECTIONS_PORT, type=int, nargs='?')
    compare.add_argument('-a', default='', nargs='?')
    area_name = compare.parse_args(sys.argv[1:])
    listen_address = area_name.a
    listen_port = area_name.p

    if listen_port == (range(1024, 65536)):
        SERVER_LOGGER.critical(f'Попытка запуска сервера с неподходящим портом: {listen_port}. '
                               f'Допустимые номера портов с 1024 до 65535.')
        sys.exit(1)

    return listen_address, listen_port


def main():
    listen_address, listen_port = create_arg_parser()

    SERVER_LOGGER.info(f'Запущен сервер, порт для подключений: {listen_port}, '
                       f'адрес входящих подключений: {listen_address}. '
                       f'Если адрес не указан, принимаются подключения с любых адресов.')

    # Готовим сокет
    transmit = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    transmit.bind((listen_address, listen_port))
    transmit.settimeout(0.3)

    # Список клиентов и их сообщений
    subscribers = []
    messages = []

    # Слушаем порт
    transmit.listen(MAX_TURN_CONNECTIONS)

    while True:
        try:
            subscriber, subscriber_address = transmit.accept()
        except OSError:
            pass
        else:
            SERVER_LOGGER.info(f'Установлено соединение с ПК: {subscriber_address}')
            subscribers.append(subscriber)

        recv_data_list = []
        send_data_list = []
        error_data_list = []
        try:
            if subscribers:
                recv_data_list, send_data_list, error_data_list = select.select(subscribers, subscribers, [], 0)
        except OSError:
            pass

        if recv_data_list:
            for sub_with_message in recv_data_list:
                try:
                    process_client_message(listen_message(sub_with_message), messages, sub_with_message)
                except:
                    SERVER_LOGGER.info(f'Клиент: {sub_with_message.geter_name()} отключился от сервера.')
                    subscribers.remove(sub_with_message)

        if messages and send_data_list:
            message = {
                ACTION: MESSAGE,
                SENDER: messages[0][0],
                TIME: time.time(),
                MESSAGE_TEXT: messages[0][1]
            }
            del messages[0]
            for waiting_sub in send_data_list:
                try:
                    send_message(waiting_sub, message)
                except:
                    SERVER_LOGGER.info(f'Клиент: {waiting_sub.geter_name()} отключился от сервера.')
                    waiting_sub.close()
                    subscribers.remove(waiting_sub)


if __name__ == '__main__':
    main()
