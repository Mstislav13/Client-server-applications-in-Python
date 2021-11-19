'''
2. Написать функцию host_range_ping() для перебора ip-адресов из заданного диапазона. Меняться должен только
   последний октет каждого адреса. По результатам проверки должно выводиться соответствующее сообщение.
'''
from subprocess import Popen, PIPE
from ipaddress import ip_address


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
            result['Reachable'] += f'{str(network_node)}'
        else:
            answer = f'Узел недоступен: {network_node}'
            result['Unreachable'] += f'{str(network_node)}'
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


host_range_ping()
