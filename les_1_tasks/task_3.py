'''
3. Написать функцию host_range_ping_tab(), возможности которой основаны на функции из примера 2. Но в данном
   случае результат должен быть итоговым по всем ip-адресам, представленным в табличном формате
   (использовать модуль tabulate). Таблица должна состоять из двух колонок и выглядеть примерно так:

   Reachable
   10.0.0.1
   10.0.0.2

   Unreachable
   10.0.0.3
   10.0.0.4
'''
from subprocess import Popen, PIPE
from ipaddress import ip_address
from tabulate import tabulate


def host_ping(_list, timeout=300):

    result = {'Reachable': '', 'Unreachable': ''}

    for network_node in _list:
        try:
            ip_address(network_node)
        except ValueError:
            pass

        _ping = Popen(f'ping {network_node} -w {timeout}', stdout=PIPE, stderr=PIPE)
        addr = _ping.wait()

        if addr == 0:
            answer = f'Узел доступен:   {network_node}'
            result['Reachable'] += f'{str(network_node)}\n'
        else:
            answer = f'Узел недоступен: {network_node}'
            result['Unreachable'] += f'{str(network_node)}\n'
        print(answer)
    return result


def host_range_ping():

    host_addr = []

    begin = input('Введите IP-адрес: ')
    quantity = input('Введите количество IP-адресов: ')

    int(begin.split('.')[-3])

    for x in range(int(quantity)):
        end = str(ip_address(begin) + x)
        host_addr.append(end)
    return host_ping(host_addr)


def host_range_ping_tab():
    dict_for_tab = host_range_ping()
    print(tabulate([dict_for_tab], headers='keys', tablefmt='pipe', stralign='left'))


host_range_ping_tab()
