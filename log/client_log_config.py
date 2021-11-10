import os
import sys
import logging
# from common.variables import LOGGING_LEVEL   # При запуске выдаёт ошибку (No module named 'common')

sys.path.append('../')

LOGGING_LEVEL = logging.DEBUG  # Перенёс сюда из-за ошибки

# Создаём формировщик логов - formatter:
CLIENT_LOG_FORMATTER = logging.Formatter('%(asctime)s %(levelname)s %(filename)s %(message)s')

# Подготовка файла для логирования
PATH = os.path.dirname(os.path.abspath(__file__))
PATH = os.path.join(PATH, 'log_data/client.log')

# Создаём потоки вывода логов
LOG_OUTPUT_STREAMS = logging.StreamHandler(sys.stderr)
LOG_OUTPUT_STREAMS.setFormatter(CLIENT_LOG_FORMATTER)
LOG_OUTPUT_STREAMS.setLevel(logging.ERROR)
LOG_FILE = logging.FileHandler(PATH, encoding='utf-8')
LOG_FILE.setFormatter(CLIENT_LOG_FORMATTER)

# Создаём и настраиваем регистратор
LOGGER = logging.getLogger('client')
LOGGER.addHandler(LOG_OUTPUT_STREAMS)
LOGGER.addHandler(LOG_FILE)
LOGGER.setLevel(LOGGING_LEVEL)

# Отладка
if __name__ == '__main__':
    LOGGER.critical('Критическая ошибка')
    LOGGER.error('Ошибка')
    LOGGER.info('Информационное сообщени')
    LOGGER.debug('Отладочная информация')
