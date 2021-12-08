import subprocess

IN = 's'              # запустить сервер
CLOSED_WINDOWS = 'x'  # закрыть все окна
EXIT = 'q'            # выход
CLIENTS = 'k'         # запустить клиентов


def main():
    """
    :return:
    """
    work_list = []
    while True:
        OPERATION = input(f'Выберите действие:\n '
                          f'{IN} - запустить сервер,\n'
                          f' {CLIENTS} - подключить клиентов,\n'
                          f' {CLOSED_WINDOWS} - закрыть все окна,\n'
                          f' {EXIT} - выход\n')

        if OPERATION == EXIT:
            break

        elif OPERATION == IN:
            # Запускаем сервер!
            work_list.append(subprocess.Popen('python server.py', creationflags=subprocess.CREATE_NEW_CONSOLE))
        elif OPERATION == 'k':
            print('Убедитесь, что на сервере зарегистрировано необходимо количество клиентов с паролем 123456.')
            print('Первый запуск может быть достаточно долгим из-за генерации ключей!')
            clients_count = int(input('Введите количество тестовых клиентов для запуска: '))
            # Запускаем клиентов:
            for _ in range(clients_count):
                work_list.append(subprocess.Popen(f'python client.py -n user{_ + 1} -p 123456',
                                                  creationflags=subprocess.CREATE_NEW_CONSOLE))
        elif OPERATION == CLOSED_WINDOWS:
            while work_list:
                work_list.pop().kill()


if __name__ == '__main__':
    main()
