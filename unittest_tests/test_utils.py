import sys
import os
import unittest
import json
sys.path.append(os.path.join(os.getcwd(), '..'))
from common.variables import ACTION, TIME, USER, ACCOUNT_NAME, PORT, PRESENCE, RESPONSE, \
    ERROR, RESPONDEFAULT_IP_ADDRESSSE, CONNECTIONS_PORT, CONNECTIONS_IP_ADDRESS, PROJECT_ENCODING
from common.utils import listen_message, send_message


class TestConnectSpot:
    '''
    тестовый класс для тестирования отправки и получения
    (при создании требует словарь, который будет прогоняться через тестовую функцию)
    '''
    def __init__(self, test_dict):
        self.test_dict = test_dict
        self.encoded_message = None
        self.received_message = None

    def transmit(self, transmit_message):
        '''
        тестовая функция отправки (корректно кодирует сообщение, сораняет то, что должно быть отправлено в сокет)
        transmit_message - отправляем в сокет
        :param transmit_message:
        :return:
        '''
        json_test_message = json.dumps(self.test_dict)
        self.encoded_message = json_test_message.encode(PROJECT_ENCODING)   # кодируем сообщение
        self.received_message = transmit_message   # сохраняем то, что должно быть отправлено в сокет

    def gotten(self, max_len):
        '''
        получаем данные из сокета
        :param max_len:
        :return:
        '''
        json_test_message = json.dumps(self.test_dict)
        return json_test_message.encode(PROJECT_ENCODING)


class TestingOfProcess(unittest.TestCase):
    '''
    тестовый класс выполняющий тестирование
    '''
    test_dict_transmit = {
        ACTION: PRESENCE,
        TIME: 1.1,
        PORT: CONNECTIONS_PORT,
        USER: {ACCOUNT_NAME: 'test_test'}
    }
    test_dict_gotten_luck = {RESPONSE: 200}
    test_dict_gotten_un_luck = {
        RESPONSE: 400,
        ERROR: 'Bad Request'
    }

    def test_send_message(self):
        '''
        тестируем корректность работы функции отправки,
        создаём тестовый сокет,
        проверяем корректность отправки словаря
        :return:
        '''
        # экземпляр тестового словаря, хранящий тестовый словарь
        test_connect_spot = TestConnectSpot(self.test_dict_transmit)
        # вызов тестируемой функции, результат которого сохранится в тестовом сокете
        send_message(test_connect_spot, self.test_dict_transmit)
        # проверка корректности кодирования словаря
        self.assertEqual(test_connect_spot.encoded_message, test_connect_spot.received_message)
        # проверка генерации исключения (если на входе будет не словарь)
        # формат assertRaises: <<self.assertRaises(TypeError, test_function, args)>>
        self.assertRaises(TypeError, send_message, test_connect_spot, 'dictionary_is_no_correct')

    def test_listen_message(self):
        '''
        тест функции приёма сообщения
        :return:
        '''
        test_connect_luck = TestConnectSpot(self.test_dict_gotten_luck)
        test_connect_un_luck = TestConnectSpot(self.test_dict_gotten_un_luck)
        # тест корректной расшифровки корректного словаря
        self.assertEqual(listen_message(test_connect_luck), self.test_dict_gotten_luck)
        # тест корректной расшифровки не корректного словаря
        self.assertEqual(listen_message(test_connect_un_luck), self.test_dict_gotten_un_luck)


if __name__ == '__main__':
    unittest.main()
