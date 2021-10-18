# 1. Каждое из слов «разработка», «сокет», «декоратор» представить в строковом формате
#    и проверить тип и содержание соответствующих переменных. Затем с помощью онлайн-конвертера
#    преобразовать строковые представление в формат Unicode и также проверить тип и содержимое переменных.

first_list = ('разработка', 'сокет', 'декоратор')

for word in first_list:
    type_word = type(word)
    uni_word = word.encode('unicode_escape')
    type_uni_word = type(uni_word)
    print(f'тип: {type_word}, слово: {word}')
    print(f'тип: {type_uni_word}, слово в формате Unicode: {uni_word}\n')
