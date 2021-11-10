class RecivedIncorrectDataError(Exception):
    '''
    Исключение: от сокета получены некорректные данные.
    '''
    def __str__(self):
        return 'Получены некорректные данные от удалённого компьютера.'


class NonDictInputError(Exception):
    '''
    Исключение: аргумент функции не словарь.
    '''
    def __str__(self):
        return 'Аргумент функции должен быть словарём.'


class ReqDictMissFiledError(Exception):
    '''
    Ошибка: в принятом словаре отсутствует обязятельное поле.
    '''
    def __init__(self, missing_field):
        self.missing_field = missing_field

    def __str__(self):
        return f'В принятом словаре отсутствует обязятельное поле {self.missing_field}.'


class ServerError(Exception):
    '''
    Исключение - ошибка сервера
    '''
    def __init__(self, text):
        self.text = text

    def __str__(self):
        return self.text
