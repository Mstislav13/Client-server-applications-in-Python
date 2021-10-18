# 6. Создать текстовый файл test_file.txt, заполнить его тремя строками: «сетевое программирование»,
#    «сокет», «декоратор». Проверить кодировку файла по умолчанию. Принудительно открыть файл в формате
#    Unicode и вывести его содержимое.

import locale
import chardet

new_file = open('test_file.txt', 'w')
new_file.write("'сетевое программирование'\n'сокет'\n'декоратор'")
new_file.close()

default_encoding = locale.getpreferredencoding()
print(f'\nкодировка (по умолчанию) файла: {default_encoding}')
# определяется кодировка: cp65001

read_file = open('test_file.txt', 'rb')
open_file = read_file.read()
print(f'содержание файла:\n{open_file}')
# содержание файла: b"'\xd1\x81\xd0\xb5\xd1\x82\xd0\xb5\xd0\xb2\xd0\xbe\xd0\xb5
#                      \xd0\xbf\xd1\x80\xd0\xbe\xd0\xb3\xd1\x80\xd0\xb0\xd0\xbc\xd0\xbc\xd0\xb8\xd1\x80
#                      \xd0\xbe\xd0\xb2\xd0\xb0\xd0\xbd\xd0\xb8\xd0\xb5'\r\n'\xd1\x81\xd0\xbe\xd0\xba\xd0
#                      \xb5\xd1\x82'\r\n'\xd0\xb4\xd0\xb5\xd0\xba\xd0\xbe\xd1\x80\xd0\xb0\xd1\x82\xd0\xbe\xd1\x80'"

print(f'кодировка: {chardet.detect(open_file)}')
# кодировка: {'encoding': 'utf-8', 'confidence': 0.99, 'language': ''}

sssss = open('test_file.txt', encoding='utf-8', errors='replace')
print(f'содержание файла:\n{sssss.read()}')
# содержание файла:
# 'сетевое программирование'
# 'сокет'
# 'декоратор'
