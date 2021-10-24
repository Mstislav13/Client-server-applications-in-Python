"""
3. Задание на закрепление знаний по модулю yaml. Написать скрипт, автоматизирующий сохранение данных в файле
   YAML-формата. Для этого:

a. Подготовить данные для записи в виде словаря, в котором первому ключу соответствует список, второму — целое число,
   третьему — вложенный словарь, где значение каждого ключа — это целое число с юникод-символом, отсутствующим в
   кодировке ASCII (например, €);

b. Реализовать сохранение данных в файл формата YAML — например, в файл file.yaml. При этом обеспечить стилизацию
   файла с помощью параметра default_flow_style, а также установить возможность работы с юникодом: allow_unicode = True;

c. Реализовать считывание данных из созданного файла и проверить, совпадают ли они с исходными.
"""
import yaml

TEST_LIST = ['apple', 'ананас', 'mouth', 'cat', 'агент 47']
TEST_NUMB = 9
TEST_DICT = {'name': 'Иван', 'surname': 'Иванов', 'salary': '300 €'}
DATA_FOR_WRITE = {'list': TEST_LIST, 'digit': TEST_NUMB, 'dict': TEST_DICT}

with open('test_file.yaml', 'w', encoding='utf-8') as new_file:
    yaml.dump(DATA_FOR_WRITE, new_file, default_flow_style=False, allow_unicode=True, indent=4)

with open('test_file.yaml', encoding='utf-8') as file_new:
    TEST_FILE = yaml.load(file_new, Loader=yaml.FullLoader)
    print(f'Проверка исходного файла:\n {TEST_FILE}')
