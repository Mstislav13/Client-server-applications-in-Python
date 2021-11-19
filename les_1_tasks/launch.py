'''
4. Продолжаем работать над проектом «Мессенджер»:
   a) Реализовать скрипт, запускающий два клиентских приложения: на чтение чата и на запись в него. Уместно
      использовать модуль subprocess).
   b) Реализовать скрипт, запускающий указанное количество клиентских приложений.
'''

import subprocess

IN = 's'              # запустить сервер
CLOSED_WINDOWS = 'x'  # закрыть все окна
EXIT = 'q'            # выход
CLIENTS = 3           # количество клиентов

WORK_LIST = []

while True:
    OPERATION = input(f'Подключить {CLIENTS} клиентов:\n '
                      f'Выберите действие:\n '
                      f'{IN} - запустить сервер и подключить клиентов,\n'
                      f' {CLOSED_WINDOWS} - закрыть все окна,\n'
                      f' {EXIT} - выход\n')

    if OPERATION == EXIT:
        break

    elif OPERATION == IN:
        WORK_LIST.append(subprocess.Popen('python server.py', creationflags=subprocess.CREATE_NEW_CONSOLE))

        for _ in range(CLIENTS):
            WORK_LIST.append(subprocess.Popen(f'python client.py -n user{_+1}',
                                              creationflags=subprocess.CREATE_NEW_CONSOLE))

    elif OPERATION == CLOSED_WINDOWS:
        while WORK_LIST:
            CLOSED = WORK_LIST.pop()
            CLOSED.kill()

