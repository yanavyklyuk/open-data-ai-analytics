import pandas as pd
import os

def load_data(file_path):
    if not os.path.exists(file_path):
        print(f"Помилка: Файл {file_path} не знайдено!")
        return None

    ext = os.path.splitext(file_path)[-1].lower()

    try:
        if ext == '.xlsx':
            df = pd.read_excel(file_path)
        else:
            df = pd.read_csv(file_path)

        print(f"Успішно завантажено! Рядків: {df.shape[0]}, Колонок: {df.shape[1]}")
        return df
    except Exception as e:
        print(f"Не вдалося прочитати файл: {e}")
        return None


if __name__ == "__main__":
    path = '../data/raw/nuclear_safety_q4_2025.xlsx'
    raw_data = load_data(path)
    if raw_data is not None:
        print(raw_data.head(3))