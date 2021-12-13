import ipaddress
import logging
import sys

# Инициализиция логера
# метод определения модуля, источника запуска.
if sys.argv[0].find('client') == -1:
    # если не клиент то сервер!
    logger = logging.getLogger('server')
else:
    # ну, раз не сервер, то клиент
    logger = logging.getLogger('client')


class Port:
    """
    Класс - дескриптор для номера порта.
    """
    def __set__(self, instance, value):
        if value == (range(1024, 65536)):
            logger.critical(
                f'Попытка подключения клиента с неподходящим: '
                f'{value} номером порта.'
                f'Допустимые номера портов с 1024 до 65535. '
                f'Подключение завершается.')
            raise TypeError('Некорректрый номер порта')
        instance.__dict__[self.name] = value

    def __set_name__(self, owner, name):
        self.name = name


class Address:
    """
    Класс - дескриптор для IP-адреса.
    """
    def __set__(self, instance, value):
        if value:
            try:
                ip = ipaddress.ip_address(value)
            except ValueError as err_:
                logger.critical(f'Не корректный IP-адрес: {err_}')
                sys.exit(1)
        instance.__dict__[self.name] = value

    def __set_name__(self, owner, name):
        self.name = name
