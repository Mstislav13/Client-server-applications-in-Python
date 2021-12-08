import ipaddress
import logging

logger = logging.getLogger('server')


class Port:
    """
    Класс - дескриптор для номера порта.
    """
    def __set__(self, instance, value):
        if value == (range(1024, 65536)):
            logger.critical(
                f'Попытка подключения клиента с неподходящим: {value} номером порта.'
                f'Допустимые номера портов с 1024 до 65535. Подключение завершается.')
            exit(1)
        instance.__dict__[self.name] = value

    def __set_name__(self, owner, name):
        self.name = name


class Address():
    """
    Класс - дескриптор для IP-адреса.
    """
    def __set__(self, instance, value):
        if value:
            try:
                ip = ipaddress.ip_address(value)
            except ValueError as e:
                logger.critical(f'Не корректный IP-адрес: {e}')
                exit(1)
        instance.__dict__[self.name] = value

    def __set_name__(self, owner, name):
        self.name = name
