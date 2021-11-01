import socket
import sys
import json
import argparse
import logging
import log.server_log_config
from errors import RecivedIncorrectDataError
from common.variables import ACTION, ACCOUNT_NAME, RESPONSE, MAX_TURN_CONNECTIONS, \
    PRESENCE, TIME, PORT, USER, ERROR, CONNECTIONS_PORT, RESPONDEFAULT_IP_ADDRESSSE
from common.utils import listen_message, send_message

# Инициализация логирования сервера
SERVER_LOGGER = logging.getLogger('server')


def process_client_message(message):
    '''
    Обработчик сообщений от клиентов, принимает словарь -
    сообщение от клинта, проверяет корректность,
    возвращает словарь-ответ для клиента
    '''
    SERVER_LOGGER.debug(f'Обработка сообщения от клиента: {message}')
    if ACTION in message and message[ACTION] == PRESENCE and TIME in message \
            and PORT in message and USER in message and message[USER][ACCOUNT_NAME] == 'Guest':
        return {RESPONSE: 200}
    return {
        RESPONDEFAULT_IP_ADDRESSSE: 400,
        ERROR: 'Bad Request'
    }


def create_arg_parser():
    '''
    Создание парсера аргументов командной строки
    '''
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', default=CONNECTIONS_PORT, type=int, nargs='?')
    parser.add_argument('-a', default='', nargs='?')
    return parser


def main():
    '''
    Загрузка параметров командной строки, если нет параметров, то задаём значения по умоланию.
    '''
    parser = create_arg_parser()
    namespace = parser.parse_args(sys.argv[1:])
    listen_address = namespace.a
    listen_port = namespace.p

    # Проверяем подходящий номер порта.
    if not 1023 < listen_port < 65536:
        SERVER_LOGGER.critical(f'Попытка запуска сервера с неподходящим портом: {listen_port}. '
                               f'Допустимые номера портов с 1024 до 65535.')
        sys.exit(1)
    SERVER_LOGGER.info(f'Запущен сервер, порт для подключений: {listen_port}, '
                       f'адрес входящих подключений: {listen_address}. '
                       f'Если адрес не указан, принимаются подключения с любых адресов.')

    # Готовим сокет
    transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    transport.bind((listen_address, listen_port))

    # Слушаем порт
    transport.listen(MAX_TURN_CONNECTIONS)

    while True:
        client, client_address = transport.accept()
        SERVER_LOGGER.info(f'Установлено соединение с ПК: {client_address}')
        try:
            message_from_client = listen_message(client)
            SERVER_LOGGER.debug(f'Получено сообщение: {message_from_client}')
            response = process_client_message(message_from_client)
            SERVER_LOGGER.info(f'Сформирован ответ клиенту: {response}')
            send_message(client, response)
            SERVER_LOGGER.debug(f'Завершение сеанса соединения с клиентом: {client_address}')
            client.close()
        except json.JSONDecodeError:
            SERVER_LOGGER.error(f'Не удалось декодировать JSON строку полученную от клиента {client_address}. '
                                f'Завершение сеанса соединения.')
            client.close()
        except RecivedIncorrectDataError:
            SERVER_LOGGER.error(f'От клиента: {client_address} приняты некорректные данные. '
                                f'Завершение сеанса соединения.')
            client.close()


if __name__ == '__main__':
    main()
