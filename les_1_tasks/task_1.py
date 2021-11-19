'''
1. Написать функцию host_ping(), в которой с помощью утилиты ping будет проверяться доступность сетевых узлов.
   Аргументом функции является список, в котором каждый сетевой узел должен быть представлен именем хоста или
   ip-адресом. В функции необходимо перебирать ip-адреса и проверять их доступность с выводом соответствующего
   сообщения («Узел доступен», «Узел недоступен»). При этом ip-адрес сетевого узла должен создаваться с помощью
   функции ip_address().
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


host_or_addr = ['yandex.ru', 'google.com', '10.10.10.10', '91.109.200.200', '192.168.88.155',
                '17.85.00.01', 'mail.ru', '192.168.100.1', '8.8.4.4', '1.1.1.1']
host_ping(host_or_addr)
