"""Утилиты"""

import json
from common.variables import MAX_LENGTH_MESSAGE, PROJECT_ENCODING


def listen_message(client):
    '''
    Утилита приёма и декодирования сообщения
    принимает байты выдаёт словарь, если приняточто-то другое отдаёт ошибку значения
    :param client:
    :return:
    '''

    encoded_response = client.recv(MAX_LENGTH_MESSAGE)
    if isinstance(encoded_response, bytes):
        json_response = encoded_response.decode(PROJECT_ENCODING)
        response = json.loads(json_response)
        if isinstance(response, dict):
            return response
        raise ValueError
    raise ValueError


def send_message(sock, message):
    '''
    Утилита кодирования и отправки сообщения
    принимает словарь и отправляет его
    :param sock:
    :param message:
    :return:
    '''

    if not isinstance(message, dict):
        raise  TypeError
    js_message = json.dumps(message)
    encoded_message = js_message.encode(PROJECT_ENCODING)
    sock.send(encoded_message)
