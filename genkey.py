import secrets

def generate_keys():
    print("=== Генератор криптографических ключей  ===")
    
    # 1. Выбор длины ключа
    print("\nВыберите длину ключа:")
    print("1 - 128 бит (32 символа hex) -> Для AES-128")
    print("2 - 256 бит (64 символа hex) -> Для AES-256 или Кузнечика")
    
    choice = input("Ваш выбор (1 или 2): ").strip()
    
    if choice == '1':
        num_bytes = 16  # 128 бит
        algo_name = "AES-128"
    elif choice == '2':
        num_bytes = 32  # 256 бит
        algo_name = "AES-256 / Kuznechik"
    else:
        print("Ошибка: Неверный выбор. Использую по умолчанию 256 бит.")
        num_bytes = 32
        algo_name = "256-bit"

    # 2. Количество ключей
    try:
        count = int(input("Сколько ключей сгенерировать? (например, 5): "))
    except ValueError:
        count = 1

    filename = "keys.txt"

    # 3. Генерация и запись
    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"--- Generated Keys for {algo_name} ---\n")
        
        print("\nГенерирую ключи...")
        for i in range(count):
            # secrets.token_hex(n) возвращает строку из 2*n hex-символов
            key = secrets.token_hex(num_bytes)
            
            # Записываем в файл
            f.write(f"{key}\n")
            
            # Выводим на экран (первые пару штук)
            if i < 3:
                print(f"Ключ {i+1}: {key}")
        
        if count > 3:
            print("...")

    print(f"\n[УСПЕХ] Сгенерировано {count} ключей.")
    print(f"Они сохранены в файле: {filename}")
    print("Скопируйте любую строку из файла и вставьте в программу шифрования.")

if __name__ == "__main__":
    generate_keys()