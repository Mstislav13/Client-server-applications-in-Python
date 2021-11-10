import subprocess

IN = 's'
CLOSED_WINDOWS = 'x'
EXIT = 'q'
CLIENT_SEND = 1
CLIENT_LISTEN = 1

WORK_LIST = []

while True:
    OPERATION = input(f'Клиенты принимающие сообщения: {CLIENT_LISTEN} чел.\n'
                      f'Клиенты передающие сообщения: {CLIENT_SEND} чел.\n'
                      f'Выберите действие:\n {IN} - запустить сервер и подключить клиентов,\n'
                      f' {CLOSED_WINDOWS} - закрыть все окна,\n'
                      f' {EXIT} - выход\n')

    if OPERATION == EXIT:
        break

    elif OPERATION == IN:
        WORK_LIST.append(subprocess.Popen('python server.py', creationflags=subprocess.CREATE_NEW_CONSOLE))

        for i in range(CLIENT_SEND):
            WORK_LIST.append(subprocess.Popen('python client.py -m send', creationflags=subprocess.CREATE_NEW_CONSOLE))

        for i in range(CLIENT_LISTEN):
            WORK_LIST.append(subprocess.Popen('python client.py -m listen', creationflags=subprocess.CREATE_NEW_CONSOLE))

    elif OPERATION == CLOSED_WINDOWS:
        while WORK_LIST:
            CLOSED = WORK_LIST.pop()
            CLOSED.kill()
