import os
import sys
import logging
import logging.handlers
from common.variables import LOGGING_LEVEL
sys.path.append('../')
sys.path.append(os.path.join(os.getcwd(), '..'))

# создаём формировщик логов (formatter):
server_formatter = logging.Formatter(
    '%(asctime)s %(levelname)s %(filename)s %(message)s')

# Подготовка имени файла для логирования
path = os.path.dirname(os.path.abspath(__file__))
path = os.path.join(path, 'log_data/server.log')

# создаём потоки вывода логов
steam = logging.StreamHandler(sys.stderr)
steam.setFormatter(server_formatter)
steam.setLevel(logging.DEBUG)
log_file = logging.handlers.TimedRotatingFileHandler(
    path, encoding='utf-8', interval=1, when='D')
log_file.setFormatter(server_formatter)

# создаём регистратор и настраиваем его
logger = logging.getLogger('server')
logger.addHandler(steam)
logger.addHandler(log_file)
logger.setLevel(LOGGING_LEVEL)

# отладка
if __name__ == '__main__':
    logger.critical('Критическая ошибка')
    logger.error('Ошибка')
    logger.debug('Отладочная информация')
    logger.info('Информационное сообщение')
