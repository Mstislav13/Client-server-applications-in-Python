import sys
from client import create_presence, process_response_ans
from common.variables import ACTION, PRESENCE, TIME, USER, ACCOUNT_NAME, RESPONSE, ERROR
import unittest
sys.path.append('../')


class TestClient(unittest.TestCase):
    # тест коректного запроса
    def test_def_presense(self):
        test = create_presence('Guest')
        test[TIME] = 1.1  # время необходимо приравнять принудительно иначе тест никогда не будет пройден
        self.assertEqual(test, {ACTION: PRESENCE, TIME: 1.1, USER: {ACCOUNT_NAME: 'Guest'}})

    def test_luck_answer(self):
        self.assertEqual(process_response_ans({RESPONSE: 200}), '200 : OK')

    def test_un_luck_answer(self):
        self.assertEqual(process_response_ans({RESPONSE: 400, ERROR: 'Bad Request'}), '400 : Bad Request')

    def test_no_response(self):
        self.assertRaises(ValueError, process_response_ans, {ERROR: 'Bad Request'})


if __name__ == '__main__':
    unittest.main()
