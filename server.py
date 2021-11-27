import argparse
import logging
import select
import socket
import sys
import json
import time
import threading
import log.server_log_config
from errors import IncorrectDataRecivedError
from decos import log
from common.variables import DEFAULT_PORT, MAX_CONNECTIONS, WHITHER, ACTION, USER, ACCOUNT_NAME, PRESENCE, TIME, \
                             RESPONSE_200, RESPONSE_400, ERROR, MESSAGE, SENDER, MESSAGE_TEXT, EXIT
from common.utils import get_message, send_message
from descriptor import Port, Address
from metaclass import ServerVerifier
from server_database import ServerStorage


# Инициализация логирования сервера
logger = logging.getLogger('server')


class Server(threading.Thread, metaclass=ServerVerifier):
    port = Port()
    addr = Address()

    def __init__(self, listen_address, listen_port, database):
        # Параметры подключения
        self.addr = listen_address
        self.port = listen_port

        # База данных сервера
        self.database = database

        # Список клиентов и их сообщений
        self.clients = []
        self.messages = []

        # Словарь, содержащий имена пользователей и соответствующие им сокеты
        self.names = dict()

        # Конструктор предка
        super().__init__()

    @log
    def process_client_message(self, message, client):
        """
        Обработчик сообщений от клиентов, принимает словарь -
        сообщение от клинта, проверяет корректность,
        возвращает словарь-ответ для клиента
        :param message:
        :param client:
        :return:
        """
        logger.debug(f'Обработка сообщения от клиента: {message}')
        if ACTION in message and message[ACTION] == PRESENCE and TIME in message and USER in message:

            if message[USER][ACCOUNT_NAME] not in self.names.keys():
                self.names[message[USER][ACCOUNT_NAME]] = client
                client_ip, client_port = client.getpeername()
                self.database.user_login(message[USER][ACCOUNT_NAME], client_ip, client_port)
                send_message(client, RESPONSE_200)
            else:
                response = RESPONSE_400
                response[ERROR] = 'Данное имя занято.'
                send_message(client, response)
                self.clients.remove(client)
                client.close()
            return
        elif ACTION in message and message[ACTION] == MESSAGE and WHITHER in message and TIME in message \
                and SENDER in message and MESSAGE_TEXT in message:
            self.messages.append(message)
            return
        elif ACTION in message and message[ACTION] == EXIT and ACCOUNT_NAME in message:
            self.database.user_logout(message[ACCOUNT_NAME])
            self.clients.remove(self.names[ACCOUNT_NAME])
            self.names[ACCOUNT_NAME].close()
            del self.names[ACCOUNT_NAME]
            return
        else:
            response = RESPONSE_400
            response[ERROR] = 'Некорректный запрос'
            send_message(client, response)
            return

    def communicate(self):
        # Инициализация сокета
        self.connection()

        while True:
            try:
                client, client_address = self.sock.accept()
            except OSError:
                pass
            else:
                logger.info(f'Установлено соедение с ПК {client_address}')
                self.clients.append(client)

            query_data_list = []
            send_data_list = []
            error_data_list = []

            try:
                if self.clients:
                    query_data_list, send_data_list, error_data_list = select.select(self.clients, self.clients, [], 0)
            except OSError:
                pass

            if query_data_list:
                for client_with_message in query_data_list:
                    try:
                        self.process_client_message(get_message(client_with_message), client_with_message)
                    except:
                        logger.info(f'Клиент {client_with_message.getpeername()} отключился от сервера.')
                        self.clients.remove(client_with_message)

            for message in self.messages:
                try:
                    self.process_message(message, send_data_list)
                except:
                    logger.info(f'Клиент: {message[WHITHER]} отключился от сервера.')
                    self.clients.remove(self.names[message[WHITHER]])
                    del self.names[message[WHITHER]]
            self.messages.clear()

    @log
    def process_message(self, message, listen_socks):
        if message[WHITHER] in self.names and self.names[message[WHITHER]] in listen_socks:
            send_message(self.names[message[WHITHER]], message)
            logger.info(f'Сообщение отправлено пользователю: {message[WHITHER]} от пользователя {message[SENDER]}.')
        elif message[WHITHER] in self.names and self.names[message[WHITHER]] not in listen_socks:
            raise ConnectionError
        else:
            logger.error(
                f'Не зарегистрированный клиент: {message[WHITHER]}. Нельзя отправить сообщение.')

    def connection(self):
        logger.info(
                    f'Запущен сервер, порт для подключений: {self.port}, '
                    f'адрес входящих подключений: {self.addr}. '
                    f'Если адрес не указан, принимаются соединения с любых адресов.'
                    )
        # Готовим сокет
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((self.addr, self.port))
        self.sock.settimeout(0.5)

        # Слушаем порт
        self.sock.listen(MAX_CONNECTIONS)


def print_help():
    print('Поддерживаемые комманды:')
    print('users - список известных пользователей')
    print('connected - список подключенных пользователей')
    print('loghist - история входов пользователя')
    print('exit - завершение работы сервера.')
    print('help - вывод справки по поддерживаемым командам')


@log
def create_arg_parser():
    """
    Создание парсера аргументов командной строки
    :return:
    """
    compare = argparse.ArgumentParser()
    compare.add_argument('-p', default=DEFAULT_PORT, type=int, nargs='?')
    compare.add_argument('-a', default='', nargs='?')
    area_name = compare.parse_args(sys.argv[1:])
    listen_address = area_name.a
    listen_port = area_name.p
    return listen_address, listen_port


def main():
    # Загрузка параметров командной строки, если нет параметров, то задаём значения по умоланию.
    listen_address, listen_port = arg_parser()

    # Инициализация базы данных
    database = ServerStorage()

    # Создание экземпляра класса - сервера и его запуск:
    server = Server(listen_address, listen_port, database)
    server.daemon = True
    server.start()

    # Печатаем справку:
    print_help()

    # Основной цикл сервера:
    while True:
        command = input('Введите комманду: ')
        if command == 'help':
            print_help()
        elif command == 'exit':
            break
        elif command == 'users':
            for user in sorted(database.users_list()):
                print(f'Пользователь {user[0]}, последний вход: {user[1]}')
        elif command == 'connected':
            for user in sorted(database.active_users_list()):
                print(f'Пользователь {user[0]}, подключен: {user[1]}:{user[2]}, время установки соединения: {user[3]}')
        elif command == 'loghist':
            name = input('Введите имя пользователя для просмотра истории. '
                         'Для вывода всей истории, просто нажмите Enter: ')
            for user in sorted(database.login_history(name)):
                print(f'Пользователь: {user[0]} время входа: {user[1]}. Вход с: {user[2]}:{user[3]}')
        else:
            print('Команда не распознана.')


if __name__ == '__main__':
    main()
