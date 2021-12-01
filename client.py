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
    USER, RESPONSE, ERROR, DEFAULT_IP_ADDRESS, DEFAULT_PORT, GET_CONTACTS, LIST_INFO, ADD_CONTACT, USERS_REQUEST, \
    REMOVE_CONTACT
from common.utils import send_message, get_message
from errors import IncorrectDataRecivedError, ReqFieldMissingError, ServerError
from metaclass import ClientVerifier
from client_database import ClientDatabase

# Инициализация клиентского логера
logger = logging.getLogger('client')

# Объект блокировки сокета и работы с базой данных
sock_lock = threading.Lock()
database_lock = threading.Lock()


class Sender(threading.Thread, metaclass=ClientVerifier):
    """
    Класс формировки и отправки сообщений на сервер и взаимодействия с пользователем.
    """
    def __init__(self, account_name, sock, database):
        self.account_name = account_name
        self.sock = sock
        self.database = database
        super().__init__()

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

    def talk(self):
        """
        Функция запрашивает кому отправить сообщение и само сообщение, и отправляет полученные данные на сервер.
        :return:
        """
        to = input('Кому отправить: ')
        message = input('Текст сообщения: ')

        # Проверим, что получатель существует
        with database_lock:
            if not self.database.check_user(to):
                logger.error(f'Попытка отправить сообщение незарегистрированому получателю: {to}')
                return

        message_dict = {
            ACTION: MESSAGE,
            SENDER: self.account_name,
            WHITHER: to,
            TIME: time.time(),
            MESSAGE_TEXT: message
        }
        logger.debug(f'Сформирован словарь сообщения: {message_dict}')

        # Сохраняем сообщения для истории
        with database_lock:
            self.database.save_message(self.account_name, to, message)

        # Необходимо дождаться освобождения сокета для отправки сообщения
        with sock_lock:
            try:
                send_message(self.sock, message_dict)
                logger.info(f'Клиенту: {to} отправлено сообщение.')
            except OSError as err:
                if err.errno:
                    logger.critical('Потеряно соединение.')
                    exit(1)
                else:
                    logger.error('Не удалось передать сообщение. Таймаут соединения')

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
                with sock_lock:
                    try:
                        send_message(self.sock, self.if_exit())
                    except:
                        pass
                    print('Завершение соединения.')
                    logger.info('Завершение работы по команде пользователя.')
                time.sleep(0.5)
                break

            # Список контактов
            elif command == 'contacts':
                with database_lock:
                    contacts_list = self.database.get_contacts()
                for contact in contacts_list:
                    print(contact)

            # Редактирование контактов
            elif command == 'edit':
                self.edit_contacts()

            # история сообщений.
            elif command == 'history':
                self.print_history()

            else:
                print('Команда не распознана, попробойте снова. help - вывести поддерживаемые команды.')

    def print_help(self):
        """Функция выводящяя справку по использованию"""
        print('Поддерживаемые команды:')
        print(' talk - отправить сообщение.')
        print('history - история сообщений')
        print('contacts - список контактов')
        print('edit - редактирование списка контактов')
        print(' exit - выход из программы')
        print(' help - вывести подсказки по командам')

    def print_history(self):
        """
        Функция выводящяя историю сообщений
        :return:
        """
        ask = input('Показать входящие сообщения - in, исходящие - out, все - просто Enter: ')
        with database_lock:
            if ask == 'in':
                history_list = self.database.get_history(to_who=self.account_name)
                for message in history_list:
                    print(f'\nСообщение от пользователя: {message[0]} от {message[3]}:\n{message[2]}')
            elif ask == 'out':
                history_list = self.database.get_history(from_who=self.account_name)
                for message in history_list:
                    print(f'\nСообщение пользователю: {message[1]} от {message[3]}:\n{message[2]}')
            else:
                history_list = self.database.get_history()
                for message in history_list:
                    print(
                        f'\nСообщение от пользователя: {message[0]}, пользователю {message[1]} от {message[3]}\n'
                        f'{message[2]}')

    def edit_contacts(self):
        """
        Функция изменеия контактов
        :return:
        """
        ans = input('Для удаления введите del, для добавления add: ')
        if ans == 'del':
            edit = input('Введите имя удаляемного контакта: ')
            with database_lock:
                if self.database.check_contact(edit):
                    self.database.del_contact(edit)
                else:
                    logger.error('Попытка удаления несуществующего контакта.')
        elif ans == 'add':
            # Проверка на возможность такого контакта
            edit = input('Введите имя создаваемого контакта: ')
            if self.database.check_user(edit):
                with database_lock:
                    self.database.add_contact(edit)
                with sock_lock:
                    try:
                        add_contact(self.sock, self.account_name, edit)
                    except ServerError:
                        logger.error('Не удалось отправить информацию на сервер.')


class Reader(threading.Thread, metaclass=ClientVerifier):
    """
    Класс-приёмник сообщений с сервера. Принимает сообщения, выводит в консоль , сохраняет в базу.
    """
    def __init__(self, account_name, sock, database):
        self.account_name = account_name
        self.sock = sock
        self.database = database
        super().__init__()

    def run(self):
        """
        Основной цикл приёмника сообщений, принимает сообщения, выводит в консоль. Завершается при потере соединения.
        :return:
        """
        while True:
            # Отдыхаем секунду и снова пробуем захватить сокет.
            # если не сделать тут задержку, то второй поток может достаточно долго ждать освобождения сокета.
            time.sleep(1)
            with sock_lock:
                try:
                    message = get_message(self.sock)

                    # Принято некорректное сообщение
                except IncorrectDataRecivedError:
                    logger.error(f'Не удалось декодировать полученное сообщение.')
                    # Вышел таймаут соединения если errno = None, иначе обрыв соединения.
                except OSError as err:
                    if err.errno:
                        logger.critical(f'Потеряно соединение с сервером.')
                        break
                    # Проблемы с соединением
                except (ConnectionError, ConnectionAbortedError, ConnectionResetError, json.JSONDecodeError):
                    logger.critical(f'Потеряно соединение с сервером.')
                    break
                    # Если пакет корретно получен выводим в консоль и записываем в базу.
                else:
                    if ACTION in message and message[ACTION] == MESSAGE and SENDER in message and WHITHER in \
                            message and MESSAGE_TEXT in message and message[WHITHER] == self.account_name:
                        print(f'\nПолучено сообщение от пользователя {message[SENDER]}:\n{message[MESSAGE_TEXT]}')
                        # Захватываем работу с базой данных и сохраняем в неё сообщение
                        with database_lock:
                            try:
                                self.database.save_message(message[SENDER], self.account_name, message[MESSAGE_TEXT])
                            except:
                                logger.error('Ошибка взаимодействия с базой данных')

                        logger.info(f'Получено сообщение от пользователя {message[SENDER]}:\n{message[MESSAGE_TEXT]}')
                    else:
                        logger.error(f'Получено некорректное сообщение с сервера: {message}')


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
    """
    Функция разбирает ответ сервера на сообщение о присутствии, возращает 200 если все ОК
     или генерирует исключение при ошибке.
    :param message:
    :return:
    """
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

# Функция запрос контакт листа
def contacts_list_request(sock, name):
    logger.debug(f'Запрос контакт листа для пользователся {name}')
    req = {
        ACTION: GET_CONTACTS,
        TIME: time.time(),
        USER: name
    }
    logger.debug(f'Сформирован запрос {req}')
    send_message(sock, req)
    ans = get_message(sock)
    logger.debug(f'Получен ответ {ans}')
    if RESPONSE in ans and ans[RESPONSE] == 202:
        return ans[LIST_INFO]
    else:
        raise ServerError


# Функция добавления пользователя в контакт лист
def add_contact(sock, username, contact):
    logger.debug(f'Создание контакта {contact}')
    req = {
        ACTION: ADD_CONTACT,
        TIME: time.time(),
        USER: username,
        ACCOUNT_NAME: contact
    }
    send_message(sock, req)
    ans = get_message(sock)
    if RESPONSE in ans and ans[RESPONSE] == 200:
        pass
    else:
        raise ServerError('Ошибка создания контакта')
    print('Удачное создание контакта.')


# Функция запроса списка известных пользователей
def user_list_request(sock, username):
    logger.debug(f'Запрос списка известных пользователей {username}')
    req = {
        ACTION: USERS_REQUEST,
        TIME: time.time(),
        ACCOUNT_NAME: username
    }
    send_message(sock, req)
    ans = get_message(sock)
    if RESPONSE in ans and ans[RESPONSE] == 202:
        return ans[LIST_INFO]
    else:
        raise ServerError


# Функция удаления пользователя из контакт листа
def remove_contact(sock, username, contact):
    logger.debug(f'Создание контакта {contact}')
    req = {
        ACTION: REMOVE_CONTACT,
        TIME: time.time(),
        USER: username,
        ACCOUNT_NAME: contact
    }
    send_message(sock, req)
    ans = get_message(sock)
    if RESPONSE in ans and ans[RESPONSE] == 200:
        pass
    else:
        raise ServerError('Ошибка удаления клиента')
    print('Удачное удаление')


# Функция инициализатор базы данных. Запускается при запуске, загружает данные в базу с сервера.
def database_load(sock, database, username):
    # Загружаем список известных пользователей
    try:
        users_list = user_list_request(sock, username)
    except ServerError:
        logger.error('Ошибка запроса списка известных пользователей.')
    else:
        database.add_users(users_list)

    # Загружаем список контактов
    try:
        contacts_list = contacts_list_request(sock, username)
    except ServerError:
        logger.error('Ошибка запроса списка контактов.')
    else:
        for contact in contacts_list:
            database.add_contact(contact)


def main():
    """
    Загружаем параметы коммандной строки
    :return:
    """
    server_address, server_port, client_name = create_arg_parser()
    print('Клиентский модуль консольного месинджера.')

    if not client_name:
        client_name = input('Введите имя пользователя: ')
    else:
        print(f'Месинджер клиента: {client_name}.')

    logger.info(
        f'Подключен клиент. Адрес сервера пользователя: {server_address}, '
        f'номер порта: {server_port}, имя пользователя: {client_name}')

    try:
        transmit = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Таймаут 1 секунда, необходим для освобождения сокета.
        transmit.settimeout(1)
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
        # Инициализация БД
        database = ClientDatabase(client_name)
        database_load(transmit, database, client_name)

        recipient = Reader(client_name, transmit, database)
        recipient.daemon = True
        recipient.start()

        # затем запускаем отправку сообщений и взаимодействие с пользователем
        meeting_room = Sender(client_name, transmit, database)
        meeting_room.daemon = True
        meeting_room.start()
        logger.debug('Начались переговоры.')

        # Watchdog основной цикл, если один из потоков завершён, то значит или потеряно соединение или пользователь
        # ввёл exit. Поскольку все события обработываются в потоках, достаточно просто завершить цикл.
        while True:
            time.sleep(1)
            if recipient.is_alive() and meeting_room.is_alive():
                continue
            break


if __name__ == '__main__':
    main()
