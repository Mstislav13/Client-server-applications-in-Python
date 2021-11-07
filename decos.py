import sys
import logging
import log.server_log_config
import log.client_log_config
import time

# Определение модуля (источника) запуска.
# Метод find() возвращает индекс первого вхождения искомой подстроки,
#                                                   если он найден в данной строке.
# Если индекс не найден, модуль возвращает: -1

if sys.argv[0].find('client') == -1:
    LOGGER = logging.getLogger('server')
else:
    LOGGER = logging.getLogger('client')


class log(object):
    def __init__(self, function):
        self.function = function

    def __call__(self, *args, **kwargs):
        stat = time.time()
        f = self.function(*args, **kwargs)
        end = time.time()
        LOGGER.debug(f'Функция: {object.__name__} с параметрами: {args}, {kwargs}. '
                     f'Вызвана из модуля {object.__module__}. '
                     f'Время выполнения: {end-stat} секунд.')
        return f
