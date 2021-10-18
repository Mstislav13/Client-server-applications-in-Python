# 4. Преобразовать слова «разработка», «администрирование», «protocol», «standard» из строкового
#    представления в байтовое и выполнить обратное преобразование (используя методы encode и decode).

third_list = ('разработка', 'администрирование', 'protocol', 'standard')

for word in third_list:
    enc_in_byte = word.encode('utf-8')
    enc_type = type(enc_in_byte)
    dec_to_str = bytes.decode(enc_in_byte, encoding='utf-8')
    dec_type = type(dec_to_str)
    print(f'\nслово: {word}.\n тип: {enc_type}\n преобразование строки в байты: {enc_in_byte}\n'
          f' тип: {dec_type} \n преобразование байт в строки: {dec_to_str}\n')
    print('-**-'*30)
