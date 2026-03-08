import sys
import os
import struct

# (S-Box) согласно ГОСТ Р 34.12-2015
Pi = [
    [12, 4, 6, 2, 10, 5, 11, 9, 14, 8, 13, 7, 0, 3, 15, 1],
    [6, 8, 2, 3, 9, 10, 5, 12, 1, 11, 7, 13, 0, 4, 15, 14],
    [7, 11, 5, 8, 12, 4, 2, 0, 14, 1, 3, 10, 9, 15, 6, 13],
    [13, 1, 7, 4, 11, 5, 0, 15, 3, 12, 14, 6, 9, 10, 2, 8],
    [5, 10, 15, 12, 1, 13, 14, 11, 8, 3, 6, 0, 4, 7, 9, 2],
    [14, 5, 0, 15, 13, 11, 3, 6, 9, 2, 12, 7, 1, 8, 10, 4],
    [11, 13, 12, 3, 7, 14, 10, 5, 0, 9, 4, 15, 2, 8, 1, 6],
    [15, 12, 9, 7, 3, 0, 11, 4, 1, 14, 2, 13, 6, 10, 8, 5]
]

def str_to_key(key_str):
    #Преобразует hex-строку ключа в список из 8-ми 32-битных чисел.
    key_bytes = bytes.fromhex(key_str)
    if len(key_bytes) != 32:
        raise ValueError("Ошибка: Длина ключа должна быть ровно 32 байта (64 hex-символа).")
    # Разбиваем 256 бит на 8 подключей по 32 бита
    return [int.from_bytes(key_bytes[i:i+4], 'big') for i in range(0, 32, 4)]

def get_round_keys(master_key):
    #Развертывание ключей: 32 раунда.

    keys = []
    # 3 цикла прямого порядка (1-24 раунды)
    for _ in range(3):
        keys.extend(master_key)
    # 1 цикл обратного порядка (25-32 раунды)
    keys.extend(master_key[::-1])
    return keys

def t_transformation(data):
    #Нелинейное биективное преобразование (S-блоки)
    output = 0
    # Проходим по 8 полубайтам (4 бита) числа
    for i in range(8):
        # Извлекаем 4 бита
        part = (data >> (4 * i)) & 0xF
        # Заменяем по таблице и ставим на место
        output |= (Pi[i][part] << (4 * i))
    return output

def g_function(data, key):
    internal = (data + key) % (2 ** 32)
    substituted = t_transformation(internal)
    # Циклический сдвиг влево на 11
    result = ((substituted << 11) | (substituted >> 21)) & 0xFFFFFFFF
    return result

def magma_cycle(block_bytes, round_keys, mode='encrypt'):
    # Разбиваем блок на левую (L) и правую (R) части
    L = int.from_bytes(block_bytes[:4], 'big')
    R = int.from_bytes(block_bytes[4:], 'big')

    if mode == 'decrypt':
        # Для расшифровки ключи те же, но идут в обратном порядке
        round_keys = round_keys[::-1]

    for i in range(31): 
        temp = R
        R = L ^ g_function(R, round_keys[i])
        L = temp
    temp = R
    R = L ^ g_function(R, round_keys[31])
    L = temp
    # Для корректности с вектором тестов возвращаем склеенный блок
    return R.to_bytes(4, 'big') + L.to_bytes(4, 'big')

def process_file(filepath, key_hex, mode='encrypt'):
    out_path = filepath + ('.enc' if mode == 'encrypt' else '.dec')
    
    keys_list = str_to_key(key_hex)
    round_keys = get_round_keys(keys_list)
    
    print(f"Начинаю {mode} файла: {filepath}")
    
    with open(filepath, 'rb') as f_in, open(out_path, 'wb') as f_out:
        while True:
            chunk = f_in.read(8)
            if not chunk:
                break  
            # Дополнение (Padding) если блок меньше 8 байт 
            original_len = len(chunk)
            if len(chunk) < 8:
                chunk += b'\x00' * (8 - len(chunk))
            # Обработка блока
            processed_block = magma_cycle(chunk, round_keys, mode)
            f_out.write(processed_block)
            
    print(f"Готово! Результат записан в: {out_path}")
def main():
    while True:
        choice = input("\nВыберите действие (1-шифровать, 2-дешифровать, q-выход): ")
        if choice == 'q':
            break
        if choice not in ['1', '2']:
            continue
            
        mode = 'encrypt' if choice == '1' else 'decrypt'
        fpath = input("Введите путь к файлу: ").strip('"')
        
        if not os.path.exists(fpath):
            print("Файл не найден!")
            continue
            
        print("Введите ключ (64 символа hex).")
        print("Пример: ffeeddccbbaa99887766554433221100f0f1f2f3f4f5f6f7f8f9fafbfcfdfeff")
        key_input = input("Ключ: ").strip()
        try:
            process_file(fpath, key_input, mode)
        except Exception as e:
            print(f"Ошибка: {e}")

if __name__ == '__main__':
    main()