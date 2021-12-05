import sys
import logging
import argparse
import log.client_log_config
from PyQt5.QtWidgets import QApplication
from common.variables import *
from common.errors import IncorrectDataRecivedError, ReqFieldMissingError, ServerError
from common.decos import log
from client.database import ClientDatabase
from client.transport import ClientTransport
from client.main_window import ClientMainWindow
from client.start_dialog import UserNameDialog
sys.path.append('../')


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


# Основная функция клиента
if __name__ == '__main__':
    # Загружаем параметы коммандной строки
    server_address, server_port, client_name = create_arg_parser()
    print('Клиентский модуль консольного месинджера.')

    # Создаём клиентокое приложение
    client_app = QApplication(sys.argv)

    # Если имя пользователя не было указано в командной строке то запросим его
    if not client_name:
        start_dialog = UserNameDialog()
        client_app.exec_()
        # Если пользователь ввёл имя и нажал ОК, то сохраняем ведённое и
        #  удаляем объект, иначе выходим
        if start_dialog.ok_pressed:
            client_name = start_dialog.client_name.text()
            del start_dialog
        else:
            exit(0)

    logger.info(
        f'Подключен клиент. Адрес сервера пользователя: {server_address}, '
        f'номер порта: {server_port}, имя пользователя: {client_name}')

    # Инициализация БД
    database = ClientDatabase(client_name)

    # Создаём объект - транспорт и запускаем транспортный поток
    try:
        transport = ClientTransport(server_port, server_address, database, client_name)
    except ServerError as error:
        print(error.text)
        exit(1)
    transport.setDaemon(True)
    transport.start()

    # Создаём GUI
    main_window = ClientMainWindow(database, transport)
    main_window.make_connection(transport)
    main_window.setWindowTitle(f'Месинджер клиента: {client_name}.')
    client_app.exec_()

    # Раз графическая оболочка закрылась, закрываем транспорт
    transport.transport_shutdown()
    transport.join()
