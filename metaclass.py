import dis


class ClientVerifier(type):
    def __init__(self, clsname, bases, clsdict):
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
                raise TypeError(f'В классе вызван запрещённый метод {command}')

        if 'get_message' in methods or 'send_message' in methods:
            pass
        else:
            raise TypeError('Отсутствуют вызовы функций, работающих с сокетами')
        super().__init__(clsname, bases, clsdict)


class ServerVerifier(type):
    def __init__(self, clsname, bases, clsdict):
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
            raise TypeError('Использование метода - connect недопустимо в серверном классе')
        if not ('SOCK_STREAM' in attributes and 'AF_INET' in attributes):
            raise TypeError('Некорректная инициализация сокета')

        super().__init__(clsname, bases, clsdict)
