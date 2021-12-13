import sys
import logging
import socket

sys.path.append('../')

# Определение модуля (источника) запуска.
# Метод find() возвращает индекс первого вхождения искомой подстроки,
# если он найден в данной строке.
# Если индекс не найден, модуль возвращает: -1

if sys.argv[0].find('client') == -1:
    logger = logging.getLogger('server')
else:
    logger = logging.getLogger('client')


def log(log_function):
    """
    :param log_function:
    :return:
    """
    def log_ing(*args, **kwargs):
        """
        :param args:
        :param kwargs:
        :return:
        """
        logger.debug(f'Функция: {log_function.__name__} '
                     f'с параметрами: {args} , {kwargs}. '
                     f'Вызов из модуля {log_function.__module__}')
        func_ = log_function(*args, **kwargs)
        return func_
    return log_ing


def login_required(func):
    """
    Декоратор, проверяющий, что клиент авторизован на сервере.
    Проверяет, что передаваемый объект сокета находится в
    списке авторизованных клиентов.
    За исключением передачи словаря-запроса
    на авторизацию. Если клиент не авторизован,
    генерирует исключение TypeError
    """
    def checker(*args, **kwargs):
        """
        Проверяем, что первый аргумент - экземпляр MessageProcessor
        Импортить необходимо тут, иначе ошибка рекурсивного импорта.
        :param args:
        :param kwargs:
        :return:
        """
        from server.core import MessageProcessor
        from client.common.variables import ACTION, PRESENCE
        if isinstance(args[0], MessageProcessor):
            found = False
            for arg in args:
                if isinstance(arg, socket.socket):
                    # Проверяем, что данный сокет есть в списке names класса
                    # MessageProcessor
                    for client in args[0].names:
                        if args[0].names[client] == arg:
                            found = True

            # Теперь надо проверить, что передаваемые аргументы не presence
            # сообщение. Если presense, то разрешаем
            for arg in args:
                if isinstance(arg, dict):
                    if ACTION in arg and arg[ACTION] == PRESENCE:
                        found = True
            # Если не не авторизован и не сообщение начала авторизации, то
            # вызываем исключение.
            if not found:
                raise TypeError
        return func(*args, **kwargs)
    return checker
