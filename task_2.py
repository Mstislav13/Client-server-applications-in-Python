"""
2. Задание на закрепление знаний по модулю json. Есть файл orders в формате JSON с информацией о заказах.
   Написать скрипт, автоматизирующий его заполнение данными. Для этого:

a. Создать функцию write_order_to_json(), в которую передается 5 параметров — товар (item), количество (quantity),
   цена (price), покупатель (buyer), дата (date). Функция должна предусматривать запись данных в виде словаря в файл
   orders.json. При записи данных указать величину отступа в 4 пробельных символа;

b. Проверить работу программы через вызов функции write_order_to_json() с передачей в нее значений каждого параметра.
"""
import json
from random import choice


def gener_order():
    item = ''
    quantity = ''
    price = ''
    buyer = ''
    date = ''

    names = ['Иван Петров', 'Пётр Иванов', 'Дмитрий Сергеев', 'Анастасия Романова']
    how_many = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10']
    how_match = ['100', '150', '200', '250', '300', '350']
    thing = ['яблоко', 'ананас', 'груша', 'слива', 'апельсин']
    pay_date = ['23.10.2021', '24.10.2021', '22.10.2021', '21.10.2021']

    for i in range(1):
        item += choice(thing)

    for i in range(1):
        quantity += choice(how_many)

    for i in range(1):
        price += choice(how_match)

    for i in range(1):
        buyer += choice(names)

    for i in range(1):
        date += choice(pay_date)

    order = {
        'item': item,
        'quantity': quantity,
        'price': price,
        'buyer': buyer,
        'date': date
    }
    return order


def main():
    orders = []

    for i in range(5):
        orders.append(gener_order())

    orders = {
        'orders': orders
    }

    with open('orders.json', 'w') as file:
        json.dump(orders, file, indent=4, ensure_ascii=False)


if __name__ == '__main__':
    main()
