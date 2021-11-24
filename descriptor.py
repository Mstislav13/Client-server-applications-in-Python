import logging

logger = logging.getLogger('server')


class Port:
    def __set__(self, instance, value):
        if value == (range(1024, 65536)):
            logger.critical(
                f'Попытка подключения клиента с неподходящим: {value} номером порта.'
                f'Допустимые номера портов с 1024 до 65535. Подключение завершается.')
            exit(1)
        instance.__dict__[self.name] = value

    def __set_name__(self, owner, name):
        self.name = name
