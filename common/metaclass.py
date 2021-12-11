import dis


class ClientVerifier(type):
    """
    Метакласс, проверяющий что в результирующем классе нет серверных
    вызовов таких как: accept, listen. Также проверяется, что сокет не
    создаётся внутри конструктора класса.
    """
    def __init__(cls, clsname, bases, clsdict):
        methods = []

        for func in clsdict:
            try:
                things = dis.get_instructions(clsdict[func])
            except TypeError:
                pass
            else:
                for i in things:
                    if i.opname == 'LOAD_GLOBAL':
                        if i.argval not in methods:
                            methods.append(i.argval)

        for command in ('accept', 'listen', 'socket'):
            if command in methods:
                raise TypeError(
                    f'В классе вызван запрещённый метод {command}')

        if 'get_message' in methods or 'send_message' in methods:
            pass
        else:
            raise TypeError(
                'Отсутствуют вызовы функций, работающих с сокетами')
        super().__init__(clsname, bases, clsdict)


class ServerVerifier(type):
    """
    Метакласс, проверяющий что в результирующем классе нет клиентских
    вызовов таких как: connect. Также проверяется, что серверный
    сокет является TCP и работает по IPv4 протоколу.
    """
    def __init__(cls, clsname, bases, clsdict):
        methods = []
        attributes = []

        for func in clsdict:
            try:
                things = dis.get_instructions(clsdict[func])
            except TypeError:
                pass
            else:
                for i in things:
                    if i.opname == 'LOAD_GLOBAL':
                        if i.argval not in methods:
                            methods.append(i.argval)
                    if i.opname == 'LOAD_ATTR':
                        if i.argval not in attributes:
                            attributes.append(i.argval)

        if 'connect' in methods:
            raise TypeError('Использование метода - '
                            'connect недопустимо в серверном классе')
        if not ('SOCK_STREAM' in attributes and 'AF_INET' in attributes):
            raise TypeError('Некорректная инициализация сокета')

        super().__init__(clsname, bases, clsdict)
