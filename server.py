import argparse
import os
import sys
import configparser
from common.decos import log
from common.utils import get_message, send_message
from common.variables import *
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from server.database import ServerStorage
from server.core import MessageProcessor
from server.main_window import MainWindow

# Инициализация логирования сервера
logger = logging.getLogger('server')


@log
def create_arg_parser(default_port, default_address):
    """
    Создание парсера аргументов командной строки
    :return:
    """
    logger.debug(f'Создание парсера аргументов командной строки: {sys.argv}')
    compare = argparse.ArgumentParser()
    compare.add_argument('-p', default=default_port, type=int, nargs='?')
    compare.add_argument('-a', default=default_address, nargs='?')
    compare.add_argument('--no_gui', action='store_true')
    area_name = compare.parse_args(sys.argv[1:])
    listen_address = area_name.a
    listen_port = area_name.p
    gui_flag = area_name.no_gui
    logger.debug('Аргументы успешно загружены')
    return listen_address, listen_port, gui_flag


@log
def config_load():
    """
    Загрузка файла конфигурации
    :return:
    """
    config = configparser.ConfigParser()
    dir_path = os.path.dirname(os.path.realpath(__file__))
    config.read(f"{dir_path}/{'server.ini'}")
    # Если файл конфигурации загружен правильно - запускаемся.
    # Иначе конфигурация по умолчанию.
    if 'SETTINGS' in config:
        return config
    else:
        config.add_section('SETTINGS')
        config.set('SETTINGS', 'Default_port', str(DEFAULT_PORT))
        config.set('SETTINGS', 'Listen_Address', '')
        config.set('SETTINGS', 'Database_path', '')
        config.set('SETTINGS', 'Database_file', 'server_base.db3')
        return config


@log
def main():
    """
    Основная функция
    :return:
    """
    # Загрузка файла конфигурации сервера
    config = config_load()

    # Загрузка параметров командной строки, если нет параметров, то задаём значения по умоланию.
    listen_address, listen_port, gui_flag = create_arg_parser(config['SETTINGS']['Default_port'],
                                                              config['SETTINGS']['Listen_Address'])

    # Инициализация базы данных
    database = ServerStorage(os.path.join(
            config['SETTINGS']['Database_path'],
            config['SETTINGS']['Database_file']))

    # Создание экземпляра класса - сервера и его запуск:
    server = MessageProcessor(listen_address, listen_port, database)
    server.daemon = True
    server.start()

    # Если  указан параметр без GUI то запускаем простенький обработчик консольного ввода
    if gui_flag:
        while True:
            command = input('Введите "exit" для завершения работы сервера.')
            if command == 'exit':
                # Если выход, то завршаем основной цикл сервера.
                server.running = False
                server.join()
                break
    # Если не указан запуск без GUI, то запускаем GUI:
    else:
        # Создаём графическое окуружение для сервера:
        server_app = QApplication(sys.argv)
        server_app.setAttribute(Qt.AA_DisableWindowContextHelpButton)
        main_window = MainWindow(database, server, config)

        # Запускаем GUI
        server_app.exec_()

        # По закрытию окон останавливаем обработчик сообщений
        server.running = False


if __name__ == '__main__':
    main()
