from subprocess import Popen, CREATE_NEW_CONSOLE
import os

IN = 's'
CLOSED_WINDOWS = 'x'
EXIT = 'q'
CLIENT = 3

work_list = []  # все клиентские процессы

while True:

    user = input(f'Запустить {CLIENT} клиентов:\n {IN} - запустить сервер и подключить клиентов,\n '
                 f'{CLOSED_WINDOWS} - закрыть все окна,\n '
                 f'{EXIT} - выход\n')

    if user == EXIT:  # если пользователь ввел q, то останавливаем цикл
        break

    elif user == IN:  # если пользователь ввел s, то запускаем процессы в консоли
        work_list.append(Popen('python server.py', creationflags=CREATE_NEW_CONSOLE))

        for _ in range(CLIENT):
            work_list.append(Popen('python client_w_r.py -m communication', creationflags=CREATE_NEW_CONSOLE))

    elif user == CLOSED_WINDOWS:   # если пользователь ввел x, то закрываем окна

        for process in work_list:
            process.kill()
            work_list.clear()  # очищаем список
