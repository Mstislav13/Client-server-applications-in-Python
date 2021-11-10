import sys
import os
import unittest

sys.path.append(os.path.join(os.getcwd(), '..'))

from common.variables import ACTION, TIME, USER, ACCOUNT_NAME, PORT, PRESENCE, RESPONSE, \
    ERROR, RESPONDEFAULT_IP_ADDRESSSE, CONNECTIONS_PORT
from client import create_presence, answer_server


class TestClient(unittest. TestCase):
    def test_def_presence(self):
        test = create_presence()
        '''время необходимо прировнять принудительно, иначе тест никогда не будет пройден'''
        test[TIME] = 1.1
        self.assertEqual(test, {ACTION: PRESENCE, TIME: 1.1, PORT: CONNECTIONS_PORT, USER: {ACCOUNT_NAME: 'Guest'}})

    def test_luck_answer(self):
        self.assertEqual(answer_server({RESPONSE: 200}), '200 : OK')

    def test_un_luck_answer(self):
        self.assertEqual(answer_server({RESPONSE: 400, ERROR: 'Bad Request'}), '400 : Bad Request')

    def test_no_response(self):
        self.assertRaises(ValueError, answer_server, {ERROR: 'Bad Request'})


if __name__ == '__main__':
    unittest.main()
