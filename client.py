import json
import socket
import sys
import time
import argparse
import logging
import threading
import log.client_log_config
from decos import log
from common.variables import ACTION, EXIT, TIME, ACCOUNT_NAME, MESSAGE, SENDER, WHITHER, MESSAGE_TEXT, PRESENCE, \
    USER, RESPONSE, ERROR, DEFAULT_IP_ADDRESS, DEFAULT_PORT
from common.utils import send_message, get_message
from errors import IncorrectDataRecivedError, ReqFieldMissingError, ServerError
from metaclass import ClientVerifier

# Инициализация клиентского логера
logger = logging.getLogger('client')


class Sender(threading.Thread, metaclass=ClientVerifier):
    def __init__(self, account_name, sock):
        self.account_name = account_name
        self.sock = sock
        super().__init__()

    def run(self):
        """
        Функция взаимодействия с пользователем
        :return:
        """
        self.print_help()
        while True:
            command = input('Введите команду: ')
            if command == 'talk':
                self.talk()
            elif command == 'help':
                self.print_help()
            elif command == 'exit':
                try:
                    send_message(self.sock, self.if_exit())
                except:
                    pass
                print('Завершение соединения.')
                logger.info('Завершение работы по команде пользователя.')
                time.sleep(0.5)
                break
            else:
                print('Команда не распознана, попробойте снова. help - вывести поддерживаемые команды.')

    def talk(self):
        to = input('Кому отправить: ')
        message = input('Текст сообщения: ')
        message_dict = {
            ACTION: MESSAGE,
            SENDER: self.account_name,
            WHITHER: to,
            TIME: time.time(),
            MESSAGE_TEXT: message
        }
        logger.debug(f'Сформирован словарь сообщения: {message_dict}')
        try:
            send_message(self.sock, message_dict)
            logger.info(f'Клиенту: {to} отправлено сообщение.')
        except:
            logger.critical('Потеряно соединение.')
            exit(1)

    def print_help(self):
        """Функция выводящяя справку по использованию"""
        print('Поддерживаемые команды:')
        print(' talk - отправить сообщение.')
        print(' exit - выход из программы')
        print(' help - вывести подсказки по командам')

    def if_exit(self):
        """
        Функция создаёт словарь с сообщением о выходе
        :return:
        """
        return {
            ACTION: EXIT,
            TIME: time.time(),
            ACCOUNT_NAME: self.account_name
        }


class Reader(threading.Thread, metaclass=ClientVerifier):
    def __init__(self, account_name, sock):
        self.account_name = account_name
        self.sock = sock
        super().__init__()

    def run(self):
        while True:
            try:
                message = get_message(self.sock)
                if ACTION in message and message[ACTION] == MESSAGE and SENDER in message and WHITHER in message \
                        and MESSAGE_TEXT in message and message[WHITHER] == self.account_name:
                    print(f'\nПолучено сообщение от пользователя {message[SENDER]}:\n{message[MESSAGE_TEXT]}')
                    logger.info(f'Получено сообщение от пользователя {message[SENDER]}:\n{message[MESSAGE_TEXT]}')
                else:
                    logger.error(f'Получено некорректное сообщение с сервера: {message}')
            except IncorrectDataRecivedError:
                logger.error(f'Не удалось декодировать полученное сообщение.')
            except (OSError, ConnectionError, ConnectionAbortedError, ConnectionResetError, json.JSONDecodeError):
                logger.critical(f'Потеряно соединение с сервером.')
                break


@log
def create_presence(account_name):
    """Запрос о нахождении клиента в сети"""
    out = {
        ACTION: PRESENCE,
        TIME: time.time(),
        USER: {
            ACCOUNT_NAME: account_name
        }
    }
    logger.debug(f'Сформировано {PRESENCE} сообщение для пользователя {account_name}')
    return out


@log
def process_response_answer(message):
    logger.debug(f'Серверное сообщение: {message}')
    if RESPONSE in message:
        if message[RESPONSE] == 200:
            return '200 : OK'
        elif message[RESPONSE] == 400:
            raise ServerError(f'400 : {message[ERROR]}')
    raise ReqFieldMissingError(RESPONSE)


@log
def create_arg_parser():
    """
    Создание парсера аргументов командной строки
    :return:
    """
    compare = argparse.ArgumentParser()
    compare.add_argument('addr', default=DEFAULT_IP_ADDRESS, nargs='?')
    compare.add_argument('port', default=DEFAULT_PORT, type=int, nargs='?')
    compare.add_argument('-n', '--name', default=None, nargs='?')
    area_name = compare.parse_args(sys.argv[1:])
    server_address = area_name.addr
    server_port = area_name.port
    client_name = area_name.name

    # проверим подходящий номер порта
    if server_port == (range(1024, 65536)):
        logger.critical(
            f'Попытка подключения клиента с неподходящим: {server_port} номером порта.'
            f'Допустимые номера портов с 1024 до 65535. Подключение завершается.')
        exit(1)

    return server_address, server_port, client_name


def main():
    """
    Загружаем параметы коммандной строки
    :return:
    """
    server_address, server_port, client_name = create_arg_parser()
    print('Клиентский модуль консольного месинджера.')
    print(f'Месинджер клиента: {client_name}.')

    if not client_name:
        client_name = input('Введите имя пользователя: ')

    logger.info(
        f'Подключен клиент. Адрес сервера пользователя: {server_address}, '
        f'номер порта: {server_port}, имя пользователя: {client_name}')

    try:
        transmit = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        transmit.connect((server_address, server_port))
        send_message(transmit, create_presence(client_name))
        answer = process_response_answer(get_message(transmit))
        logger.info(f'Принят ответ от сервера: {answer}')
        print(f'Установлено соединение с сервером')
    except json.JSONDecodeError:
        logger.error('Не удалось декодировать полученную Json строку.')
        exit(1)
    except ServerError as error:
        logger.error(f'При установке соединения сервер вернул ошибку: {error.text}')
        exit(1)
    except ReqFieldMissingError as missing_error:
        logger.error(f'В ответе сервера отсутствует необходимое поле {missing_error.missing_field}')
        exit(1)
    except (ConnectionRefusedError, ConnectionError):
        logger.critical(
            f'Не удалось подключиться к серверу {server_address}:{server_port}, '
            f'сервер отклонил запрос на подключение.')
        exit(1)
    else:
        recipient = Reader(client_name, transmit)
        recipient.daemon = True
        recipient.start()

        # затем запускаем отправку сообщений и взаимодействие с пользователем
        meeting_room = Sender(client_name, transmit)
        meeting_room.daemon = True
        meeting_room.start()
        logger.debug('Начались переговоры.')

        while True:
            time.sleep(1)
            if recipient.is_alive() and meeting_room.is_alive():
                continue
            break


if __name__ == '__main__':
    main()
