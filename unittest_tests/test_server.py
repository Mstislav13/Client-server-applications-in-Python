import sys
import os
import unittest
sys.path.append(os.path.join(os.getcwd(), '..'))
from common.variables import ACTION, TIME, USER, ACCOUNT_NAME, PORT, PRESENCE, RESPONSE, \
    ERROR, RESPONDEFAULT_IP_ADDRESSSE, CONNECTIONS_PORT
from server import process_client_message


class TestServer(unittest.TestCase):
    dict_luck = {RESPONSE: 200}
    dict_un_luck = {
        RESPONSE: 400,
        ERROR: 'Bad Request'
    }

    def test_luck_check(self):
        self.assertEqual(process_client_message({ACTION: PRESENCE, TIME: 1.1, PORT: CONNECTIONS_PORT,
                                                 USER: {ACCOUNT_NAME: 'Guest'}}), self.dict_luck)

    def test_un_luck_check(self):
        self.assertNotEqual(process_client_message({ACTION: PRESENCE, TIME: 1.1, PORT: CONNECTIONS_PORT,
                                                    USER: {ACCOUNT_NAME: 'Guest'}}), self.dict_un_luck)

    def test_wrong_message(self):
        self.assertNotEqual(process_client_message({ACTION: PRESENCE}), self.dict_luck)

    def test_half_message(self):
        self.assertNotEqual(process_client_message({ACTION: PRESENCE, TIME: 1.1}), self.dict_luck)

    def test_no_user(self):
        self.assertNotEqual(process_client_message({ACTION: PRESENCE, TIME: 1.1, PORT: CONNECTIONS_PORT}),
                            self.dict_luck)

    def test_unknown_user(self):
        self.assertNotEqual(process_client_message({ACTION: PRESENCE, TIME: 1.1, PORT: CONNECTIONS_PORT,
                                                    USER: {ACCOUNT_NAME: 'Ivan'}}), self.dict_luck)


if __name__ == '__main__':
    unittest.main()
