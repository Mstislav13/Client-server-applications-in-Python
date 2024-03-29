import subprocess

IN = 's'  # запустить сервер
CLOSED_WINDOWS = 'x'  # закрыть все окна
EXIT = 'q'  # выход
# CLIENTS = 3           # количество клиентов

WORK_LIST = []

while True:
    operation = input(f'Выберите действие:\n '
                      f'{IN} - запустить сервер и подключить клиентов,\n'
                      f' {CLOSED_WINDOWS} - закрыть все окна,\n'
                      f' {EXIT} - выход\n')

    if operation == EXIT:
        break

    elif operation == IN:
        CLIENTS = int(input('Сколько клиентов запустить?: '))
        WORK_LIST.append(subprocess.Popen('python server.py',
                                          creationflags=subprocess.
                                          CREATE_NEW_CONSOLE))

        for _ in range(CLIENTS):
            WORK_LIST.append(
                subprocess.Popen(f'python client.py -n user{_ + 1} -p 123456',
                                 creationflags=subprocess.CREATE_NEW_CONSOLE))

    elif operation == CLOSED_WINDOWS:
        while WORK_LIST:
            CLOSED = WORK_LIST.pop()
            CLOSED.kill()
