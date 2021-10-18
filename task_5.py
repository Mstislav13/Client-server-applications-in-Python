# 5. Выполнить пинг веб-ресурсов yandex.ru, youtube.com и преобразовать результаты из байтовового
#    в строковый тип на кириллице.

import subprocess
import chardet

web_res = [['ping', 'yandex.ru'], ['ping', 'youtube.com']]

for ping in web_res:
    ping_process = subprocess.Popen(ping, stdout=subprocess.PIPE)

    for line in ping_process.stdout:
            result = chardet.detect(line)
            line = line.decode('cp866').encode('utf-8')
            print(line.decode('utf-8'))
