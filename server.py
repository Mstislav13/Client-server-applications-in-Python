import socket
import sys
import argparse
import logging
import log.server_log_config
from common.variables import ACTION, ACCOUNT_NAME, RESPONSE, MAX_TURN_CONNECTIONS, \
    PRESENCE, TIME, USER, ERROR, CONNECTIONS_PORT, RESPONDEFAULT_IP_ADDRESSSE, MESSAGE, MESSAGE_TEXT, SENDER, \
    WHITHER, EXIT, RESPONSE_200, RESPONSE_400
from common.utils import listen_message, send_message
from decos import log
import select

# Инициализация логирования сервера
SERVER_LOGGER = logging.getLogger('server')


@log
def process_client_message(message, list_message, subscriber, subscribers, names):
    '''
    Обработчик сообщений от клиентов, принимает словарь -
    сообщение от клинта, проверяет корректность,
    возвращает словарь-ответ для клиента
    '''
    SERVER_LOGGER.debug(f'Обработка сообщения от клиента: {message}')
    if ACTION in message and message[ACTION] == PRESENCE and TIME in message and USER in message:
        if message[USER][ACCOUNT_NAME] not in names.keys():
            names[message[USER][ACCOUNT_NAME]] = subscriber
            send_message(subscriber, RESPONSE_200)
        else:
            answer = RESPONSE_400
            answer[ERROR] = 'Данное имя занято.'
            send_message(subscriber, answer)
            subscribers.remove(subscriber)
            subscriber.close()
        return
    elif ACTION in message and message[ACTION] == MESSAGE and WHITHER in message and TIME in \
            message and SENDER in message and MESSAGE_TEXT in message:
        list_message.append(message)
        return
    elif ACTION in message and message[ACTION] == EXIT and ACCOUNT_NAME in message:
        subscribers.remove(names[message[ACCOUNT_NAME]])
        names[message[ACCOUNT_NAME]].close()
        del names[message[ACCOUNT_NAME]]
        return
    else:
        answer = RESPONSE_400
        answer[ERROR] = 'Некорректный запрос'
        send_message(subscriber, answer)
        return


@log
def whither_message(message, name, _socket):
    if message[WHITHER] in name and name[message[WHITHER]] in _socket:
        send_message(name[message[WHITHER]], message)
        SERVER_LOGGER.info(f'Сообщение отправлено клиенту: {message[WHITHER]} от клиента: {message[SENDER]}.')
    elif message[WHITHER] in name and name[message[WHITHER]] not in _socket:
        raise ConnectionError
    else:
        SERVER_LOGGER.error(
            f'Не зарегистрированный клиент: {message[WHITHER]}. Нельзя отправить сообщение.')


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
    transmit.settimeout(0.5)

    # Список клиентов и их сообщений
    subscribers = []
    messages = []

    # Словарь с именами и сокетами клиентов
    info = dict()

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

        query_data_list = []
        send_data_list = []
        error_data_list = []
        try:
            if subscribers:
                query_data_list, send_data_list, error_data_list = select.select(subscribers, subscribers, [], 0)
        except OSError:
            pass

        if query_data_list:
            for sub_with_message in query_data_list:
                try:
                    process_client_message(listen_message(sub_with_message), messages, sub_with_message,
                                           subscribers, info)
                except Exception:
                    SERVER_LOGGER.info(f'Клиент: {sub_with_message.geter_name()} отключился от сервера.')
                    subscribers.remove(sub_with_message)

        for mess in messages:
            try:
                whither_message(mess, info, send_data_list)
            except Exception:
                SERVER_LOGGER.info(f'Клиент: {mess[WHITHER]} отключился от сервера.')
                subscribers.remove(info[mess[WHITHER]])
                del info[mess[WHITHER]]
        messages.clear()


if __name__ == '__main__':
    main()
