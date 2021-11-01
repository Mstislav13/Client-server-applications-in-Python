"""
1.Задание на закрепление знаний по модулю CSV. Написать скрипт, осуществляющий выборку определенных данных
  из файлов info_1.txt, info_2.txt, info_3.txt и формирующий новый «отчетный» файл в формате CSV. Для этого:

a. Создать функцию get_data(), в которой в цикле осуществляется перебор файлов с данными, их открытие и считывание
   данных. В этой функции из считанных данных необходимо с помощью регулярных выражений извлечь значения параметров
   «Изготовитель системы», «Название ОС», «Код продукта», «Тип системы». Значения каждого параметра поместить в
   соответствующий список. Должно получиться четыре списка — например, os_prod_list, os_name_list, os_code_list,
   os_type_list. В этой же функции создать главный список для хранения данных отчета — например, main_data — и
   поместить в него названия столбцов отчета в виде списка: «Изготовитель системы», «Название ОС», «Код продукта»,
   «Тип системы». Значения для этих столбцов также оформить в виде списка и поместить в файл main_data
   (также для каждого файла);

b. Создать функцию write_to_csv(), в которую передавать ссылку на CSV-файл. В этой функции реализовать получение
   данных через вызов функции get_data(), а также сохранение подготовленных данных в соответствующий CSV-файл;

c. Проверить работу программы через вызов функции write_to_csv().
"""

import csv
import chardet
import re

FILE_1 = 'info_1.txt'
FILE_2 = 'info_2.txt'
FILE_3 = 'info_3.txt'
SEARCH_IN_FILES = [FILE_1, FILE_2, FILE_3]

REG_1 = 'Изготовитель системы'
REG_2 = 'Название ОС'
REG_3 = 'Код продукта'
REG_4 = 'Тип системы'
ALL_REG = [REG_1, REG_2, REG_3, REG_4]


def get_data():

    prod_list = []          #
    name_os_list = []       #
    code_prod_list = []     # формируем списки
    type_sys_list = []      #
    main_data = []          #

    for file in SEARCH_IN_FILES:
        with open(file, 'rb') as file_new:                       # открываем файл
            data_in_byte = file_new.read()                       # читаем файл
            total = chardet.detect(data_in_byte)                 # определяем кодировку
            dec_byte = data_in_byte.decode(total['encoding'])    # декодируем

            prod_reg = re.compile(rf'{REG_1}\s*\S*')
            prod_list.append(prod_reg.findall(dec_byte)[0].split()[2])

            name_os_reg = re.compile(rf'{REG_2}\s*\S*')
            name_os_list.append(name_os_reg.findall(dec_byte)[0].split()[2])

            code_prod_reg = re.compile(rf'{REG_3}\s*\S*')
            code_prod_list.append(code_prod_reg.findall(dec_byte)[0].split()[2])

            type_sys_reg = re.compile(rf'{REG_4}\s*\S*')
            type_sys_list.append(type_sys_reg.findall(dec_byte)[0].split()[2])

            head = ALL_REG
            main_data.append(head)

            data_in_row = [prod_list, name_os_list, code_prod_list, type_sys_list]

            for i in range(len(data_in_row[0])):
                line = [row[i] for row in data_in_row]
                main_data.append(line)

            return main_data


def write_to_csv(csv_file):
    main_data = get_data()

    with open(csv_file, 'w', encoding='utf-8') as next_file:
        csv_file_writer = csv.writer(next_file, delimiter=';')
        for row in main_data:
            csv_file_writer.writerow(row)


write_to_csv('check_file.csv')
