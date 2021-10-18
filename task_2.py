# 2. Каждое из слов «class», «function», «method» записать в байтовом типе без преобразования
#    в последовательность кодов (не используя методы encode и decode) и определить тип, содержимое
#    и длину соответствующих переменных.

second_list = (b'class', b'function', b'method')

for byte_word in second_list:
    type_byte_word = type(byte_word)
    len_byte_word = len(byte_word)
    print(f'тип: {type_byte_word}, слово: {byte_word}, длина: {len_byte_word}\n')
