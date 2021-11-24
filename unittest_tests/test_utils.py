import sys
from common.utils import get_message, send_message
from common.variables import ENCODING, ACTION, PRESENCE, TIME, USER, ACCOUNT_NAME, RESPONSE, ERROR
import unittest
from errors import NonDictInputError
import json
import os
sys.path.append('../')
sys.path.append(os.path.join(os.getcwd(), '..'))


class TestConnectSpot:
    """
    Тестовый класс для тестирования отправки и получения
    (при создании требует словарь, который будет прогоняться через тестовую функцию)
    """
    def __init__(self, test_dict):
        self.testdict = test_dict

    def send(self, message_to_send):
        """
        Тестовая функция отправки (корректно кодирует сообщение, сораняет то, что должно быть отправлено в сокет)
        transmit_message - отправляем в сокет
        :param message_to_send:
        :return:
        """
        json_test_message = json.dumps(self.testdict)
        self.encoded_message = json_test_message.encode(ENCODING)
        self.receved_message = message_to_send

    def recv(self, max_len):
        """
        Получаем данные из сокета
        :param max_len:
        :return:
        """
        json_test_message = json.dumps(self.testdict)
        return json_test_message.encode(ENCODING)


class TestingOfProcess(unittest.TestCase):
    """
    Тестовый класс выполняющий тестирование
    """
    test_dict_send = {
        ACTION: PRESENCE,
        TIME: 111111.111111,
        USER: {
            ACCOUNT_NAME: 'test_test'
        }
    }
    test_dict_gotten_luck = {RESPONSE: 200}
    test_dict_gotten_un_luck = {
        RESPONSE: 400,
        ERROR: 'Bad Request'
    }

    def test_send_message(self):
        """
        Тестируем корректность работы функции отправки,
        создаём тестовый сокет,
        проверяем корректность отправки словаря
        :return:
        """
        # экземпляр тестового словаря, хранит собственно тестовый словарь
        test_socket = TestConnectSpot(self.test_dict_send)
        # вызов тестируемой функции, результаты будут сохранены в тестовом сокете
        send_message(test_socket, self.test_dict_send)
        # проверка корретности кодирования словаря. сравниваем результат довренного кодирования и результат
        # от тестируемой функции
        self.assertEqual(test_socket.encoded_message, test_socket.receved_message)
        # дополнительно, проверим генерацию исключения, при не словаре на входе.
        self.assertRaises(NonDictInputError, send_message, test_socket, 1111)

    def test_listen_message(self):
        """
        Тест функции приёма сообщения
        :return:
        """
        test_sock_luck = TestConnectSpot(self.test_dict_gotten_luck)
        test_sock_un_luck = TestConnectSpot(self.test_dict_gotten_un_luck)
        # тест корректной расшифровки корректного словаря
        self.assertEqual(get_message(test_sock_luck), self.test_dict_gotten_luck)
        # тест корректной расшифровки ошибочного словаря
        self.assertEqual(get_message(test_sock_un_luck), self.test_dict_gotten_un_luck)


if __name__ == '__main__':
    unittest.main()
