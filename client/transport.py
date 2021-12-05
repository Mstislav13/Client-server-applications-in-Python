import socket
import os
import sys
import time
import logging
import json
import threading
from PyQt5.QtCore import pyqtSignal, QObject
from common.utils import *
from common.variables import *
from common.errors import ServerError
sys.path.append('../')

# Инициализация клиентского логера
logger = logging.getLogger('client')

# Объект блокировки сокета
socket_lock = threading.Lock()


class ClientTransport(threading.Thread, QObject):
    """
    Класс - Траннспорт, отвечает за взаимодействие с сервером
    """
    # Сигналы новое сообщение и потеря соединения
    new_message = pyqtSignal(str)
    connection_lost = pyqtSignal()

    def __init__(self, port, ip_address, database, username):
        # Вызываем конструктор предка
        threading.Thread.__init__(self)
        QObject.__init__(self)

        # Работа с базой данных
        self.database = database
        # Имя пользователя
        self.username = username
        # Сокет для работы с сервером
        self.transport = None
        # Устанавливаем соединение
        self.connection_init(port, ip_address)
        # Обновляем таблицы известных пользователей и контактов
        try:
            self.user_list_update()
            self.contacts_list_update()
        except OSError as err:
            if err.errno:
                logger.critical(f'Потеряно соединение с сервером.')
                raise ServerError('Потеряно соединение с сервером!')
            logger.error('Timeout соединения при обновлении списков пользователей.')
        except json.JSONDecodeError:
            logger.critical(f'Потеряно соединение с сервером.')
            raise ServerError('Потеряно соединение с сервером!')
        # Флаг продолжения работы транспорта.
        self.running = True

    def connection_init(self, port, ip):
        """
        Функция инициализации соединения с сервером
        :param port:
        :param ip:
        :return:
        """
        # Инициализация сокета и сообщение серверу о нашем появлении
        self.transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Таймаут необходим для освобождения сокета.
        self.transport.settimeout(5)

        # Соединяемся, 5 попыток соединения, флаг успеха ставим в True если удалось
        connected = False
        for i in range(5):
            logger.info(f'Попытка подключения №{i + 1}')
            try:
                self.transport.connect((ip, port))
            except (OSError, ConnectionRefusedError):
                pass
            else:
                connected = True
                break
            time.sleep(1)

        # Если соединится не удалось - исключение
        if not connected:
            logger.critical('Не удалось установить соединение с сервером')
            raise ServerError('Не удалось установить соединение с сервером')

        logger.debug('Установлено соединение с сервером')

        # Посылаем серверу приветственное сообщение и получаем ответ что всё нормально
        #   или ловим исключение.
        try:
            with socket_lock:
                send_message(self.transport, self.create_presence())
                self.process_response_answer(get_message(self.transport))
        except (OSError, json.JSONDecodeError):
            logger.critical('Потеряно соединение с сервером!')
            raise ServerError('Потеряно соединение с сервером!')

        # Раз всё хорошо, сообщение о установке соединения.
        logger.info('Соединение с сервером успешно установлено.')

    @log
    def create_presence(self):
        """Запрос о нахождении клиента в сети"""
        out = {
            ACTION: PRESENCE,
            TIME: time.time(),
            USER: {
                ACCOUNT_NAME: self.username
            }
        }
        logger.debug(f'Сформировано {PRESENCE} сообщение для пользователя {self.username}')
        return out

    @log
    def process_response_answer(self, message):
        """
        Функция разбирает ответ сервера на сообщение о присутствии, возращает 200 если все ОК
         или генерирует исключение при ошибке.
        :param message:
        :return:
        """
        logger.debug(f'Серверное сообщение: {message}')
        if RESPONSE in message:
            if message[RESPONSE] == 200:
                return
            elif message[RESPONSE] == 400:
                raise ServerError(f'400 : {message[ERROR]}')
            else:
                logger.debug(f'Принят неизвестный код подтверждения: {message[RESPONSE]}')

        # Если это сообщение от пользователя, добавляем в базу, даём сигнал о новом сообщении
        elif ACTION in message and message[ACTION] == MESSAGE and SENDER in message and WHITHER in message \
                and MESSAGE_TEXT in message and message[WHITHER] == self.username:
            logger.debug(f'Получено сообщение от пользователя: {message[SENDER]}:{message[MESSAGE_TEXT]}')
            self.database.save_message(message[SENDER], 'in', message[MESSAGE_TEXT])
            self.new_message.emit(message[SENDER])

    def contacts_list_update(self):
        """
        Функция обновляющая контакт-лист с сервера
        :return:
        """
        logger.debug(f'Запрос контакт-листа для пользователя: {self.name}')
        req = {
            ACTION: GET_CONTACTS,
            TIME: time.time(),
            USER: self.username
        }
        logger.debug(f'Сформирован запрос: {req}')
        with socket_lock:
            send_message(self.transport, req)
            ans = get_message(self.transport)
        logger.debug(f'Получен ответ: {ans}')
        if RESPONSE in ans and ans[RESPONSE] == 202:
            for contact in ans[LIST_INFO]:
                self.database.add_contact(contact)
        else:
            logger.error('Не удалось обновить список контактов.')

    def user_list_update(self):
        """
        Функция обновления таблицы известных пользователей.
        :return:
        """
        logger.debug(f'Запрос списка известных пользователей {self.username}')
        req = {
            ACTION: USERS_REQUEST,
            TIME: time.time(),
            ACCOUNT_NAME: self.username
        }
        with socket_lock:
            send_message(self.transport, req)
            ans = get_message(self.transport)
        if RESPONSE in ans and ans[RESPONSE] == 202:
            self.database.add_users(ans[LIST_INFO])
        else:
            logger.error('Не удалось обновить список известных пользователей.')

    def add_contact(self, contact):
        """
        Функция добавления пользователя в контакт-лист
        :param contact:
        :return:
        """
        logger.debug(f'Создание контакта: {contact}')
        req = {
            ACTION: ADD_CONTACT,
            TIME: time.time(),
            USER: self.username,
            ACCOUNT_NAME: contact
        }
        with socket_lock:
            send_message(self.transport, req)
            self.process_response_answer(get_message(self.transport))

    def remove_contact(self, contact):
        """
        Функция удаления пользователя из контакт-листа
        :param contact:
        :return:
        """
        logger.debug(f'Удаление контакта: {contact}')
        req = {
            ACTION: REMOVE_CONTACT,
            TIME: time.time(),
            USER: self.username,
            ACCOUNT_NAME: contact
        }
        with socket_lock:
            send_message(self.transport, req)
            self.process_response_answer(get_message(self.transport))

    def transport_shutdown(self):
        """
        Функция закрытия соединения, отправляет сообщение о выходе.
        :return:
        """
        self.running = False
        message = {
            ACTION: EXIT,
            TIME: time.time(),
            ACCOUNT_NAME: self.username
        }
        with socket_lock:
            try:
                send_message(self.transport, message)
            except OSError:
                pass
        logger.debug('Соединение завершается.')
        time.sleep(0.5)

    def send_message(self, to, message):
        """
        Функция отправки сообщения на сервер
        :param to:
        :param message:
        :return:
        """
        message_dict = {
            ACTION: MESSAGE,
            SENDER: self.account_name,
            WHITHER: to,
            TIME: time.time(),
            MESSAGE_TEXT: message
        }
        logger.debug(f'Сформирован словарь сообщения: {message_dict}')

        # Необходимо дождаться освобождения сокета для отправки сообщения
        with socket_lock:
            send_message(self.transport, message_dict)
            self.process_response_answer(get_message(self.transport))
            logger.info(f'Клиенту: {to} отправлено сообщение.')

    def run(self):
        """
        Основной цикл приёмника сообщений, принимает сообщения, выводит в консоль. Завершается при потере соединения.
        :return:
        """
        logger.debug('Запущен процесс - приёмник собщений с сервера.')
        while self.running:
            # Отдыхаем секунду и снова пробуем захватить сокет.
            # Если не сделать тут задержку, то второй поток может достаточно долго ждать освобождения сокета.
            time.sleep(1)
            with socket_lock:
                try:
                    self.transport.settimeout(0.5)
                    message = get_message(self.transport)
                except OSError as err:
                    if err.errno:
                        logger.critical(f'Потеряно соединение с сервером.')
                        self.running = False
                        self.connection_lost.emit()
                # Проблемы с соединением
                except (ConnectionError, ConnectionAbortedError, ConnectionResetError, json.JSONDecodeError, TypeError):
                    logger.debug(f'Потеряно соединение с сервером.')
                    self.running = False
                    self.connection_lost.emit()
                # Если сообщение получено, то вызываем функцию обработчик:
                else:
                    logger.debug(f'Принято сообщение с сервера: {message}')
                    self.process_response_answer(message)
                finally:
                    self.transport.settimeout(5)
