import pandas as pd
import sqlite3
import os
import numpy as np
from dotenv import load_dotenv

load_dotenv()

def get_db_connection():
    db_path = os.getenv('DB_PATH')
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    return sqlite3.connect(db_path)

def prepare_data(df):
    df.columns = df.columns.str.strip().str.replace(' ', '_').str.replace('__', '_')
    df['station'] = df['station'].replace('ЮУАЕС', 'ПАЕС')

    def clean_val(x):
        if pd.isna(x): return np.nan
        s = str(x).replace(',', '.').strip()
        if '<' in s:
            try:
                return float(s.replace('<', '')) - 0.001
            except:
                return np.nan
        try:
            return float(s)
        except:
            return np.nan

    num_cols = [c for c in df.columns if c not in ['year', 'quarter', 'station']]
    for col in num_cols:
        df[col] = df[col].apply(clean_val)

    if 'co_60_dump' in df.columns:
        df = df.drop(columns=['co_60_dump'])

    df = df.dropna()

    return df

def init_db(df):
    table_name = os.getenv('TABLE_NAME', 'nuclear_safety_reports')
    conn = get_db_connection()

    cols = []
    for col in df.columns:
        if col in ['year', 'quarter']:
            cols.append(f'"{col}" INTEGER NOT NULL')
        elif col == 'station':
            cols.append(f'"{col}" TEXT NOT NULL')
        else:
            cols.append(f'"{col}" REAL')

    query = f"CREATE TABLE IF NOT EXISTS \"{table_name}\" ({', '.join(cols)});"
    conn.execute(query)
    conn.commit()
    conn.close()

def load_data_from_file():
    file_path = os.getenv('RAW_DATA_PATH')
    if not os.path.exists(file_path):
        print(f"Помилка: Файл {file_path} не знайдено")
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

def load_data_to_db(df):
    if df is None:
        return
    table_name = os.getenv('TABLE_NAME', 'nuclear_safety_reports')
    conn = get_db_connection()
    try:
        conn.execute(f'DELETE FROM "{table_name}"')

        df.to_sql(table_name, conn, if_exists='append', index=False)

        conn.commit()

        print(f"Дані успішно імпортовані в SQLite.")
    except Exception as e:
        print(f"Помилка завантаження: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    raw_df = load_data_from_file()
    if raw_df is not None:
        clean_df = prepare_data(raw_df)
        init_db(clean_df)
        load_data_to_db(clean_df)
        