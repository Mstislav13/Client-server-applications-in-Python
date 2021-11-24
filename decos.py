import sys
import log.server_log_config
import log.client_log_config
import logging

# Определение модуля (источника) запуска.
# Метод find() возвращает индекс первого вхождения искомой подстроки,
#                                                   если он найден в данной строке.
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
        logger.debug(f'Функция: {log_function.__name__} с параметрами: {args} , {kwargs}. '
                     f'Вызов из модуля {log_function.__module__}')
        f = log_function(*args , **kwargs)
        return f
    return log_ing
