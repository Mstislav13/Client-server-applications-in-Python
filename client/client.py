import os
import sys
import logging
import argparse
from Cryptodome.PublicKey import RSA
from PyQt5.QtWidgets import QApplication, QMessageBox
from common.variables import DEFAULT_IP_ADDRESS, DEFAULT_PORT
from common.errors import ServerError
from common.decos import log
from client.database import ClientDatabase
from client.transport import ClientTransport
from client.main_window import ClientMainWindow
from client.start_dialog import UserNameDialog

# Инициализация клиентского логера
logger = logging.getLogger('client')


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
    compare.add_argument('-p', '--password', default='', nargs='?')
    area_name = compare.parse_args(sys.argv[1:])
    server_address = area_name.addr
    server_port = area_name.port
    client_name = area_name.name
    client_passwd = area_name.password

    # проверим подходящий номер порта
    if server_port == (range(1024, 65536)):
        logger.critical(
            f'Попытка подключения клиента с неподходящим: {server_port} '
            f'номером порта.'
            f'Допустимые номера портов с 1024 до 65535. '
            f'Подключение завершается.')
        sys.exit(1)

    return server_address, server_port, client_name, client_passwd


# Основная функция клиента
if __name__ == '__main__':
    # Загружаем параметы коммандной строки
    server_address, server_port, client_name, \
        client_passwd = create_arg_parser()
    logger.debug('Аргументы загружены.')

    # Создаём клиентокое приложение
    client_app = QApplication(sys.argv)

    # Если имя пользователя не было указано в командной строке то запросим его
    start_dialog = UserNameDialog()
    if not client_name or not client_passwd:
        client_app.exec_()
        # Если пользователь ввёл имя и нажал ОК, то сохраняем ведённое и
        # удаляем объект, инааче выходим
        if start_dialog.ok_pressed:
            client_name = start_dialog.client_name.text()
            client_passwd = start_dialog.client_passwd.text()
            logger.debug(
                f'Using USERNAME = {client_name}, PASSWD = {client_passwd}.')
        else:
            sys.exit(0)

    logger.info(
        f'Подключен клиент. Адрес сервера пользователя: {server_address}, '
        f'номер порта: {server_port}, имя пользователя: {client_name}')

    # Загружаем ключи из файла, если же файла нет, то генерируем новую пару.
    dir_path = os.getcwd()
    key_file = os.path.join(dir_path, f'{client_name}.key')
    if not os.path.exists(key_file):
        keys = RSA.generate(2048, os.urandom)
        with open(key_file, 'wb') as key:
            key.write(keys.export_key())
    else:
        with open(key_file, 'rb') as key:
            keys = RSA.import_key(key.read())
    logger.debug('Ключи успешно загружены.')

    # Инициализация БД
    database = ClientDatabase(client_name)

    # Создаём объект - транспорт и запускаем транспортный поток
    try:
        transport = ClientTransport(
            server_port,
            server_address,
            database,
            client_name,
            client_passwd,
            keys)
        logger.debug('Объект готов к транспортировке')
    except ServerError as error:
        message = QMessageBox()
        message.critical(start_dialog, 'Ошибка сервера', error.text)
        sys.exit(1)
    transport.setDaemon(True)
    transport.start()

    # Удалим объект диалога за ненадобностью
    del start_dialog

    # Создаём GUI
    main_window = ClientMainWindow(database, transport, keys)
    main_window.make_connection(transport)
    main_window.setWindowTitle(f'Месинджер клиента: {client_name}.')
    client_app.exec_()

    # Раз графическая оболочка закрылась, закрываем транспорт
    transport.transport_shutdown()
    transport.join()
