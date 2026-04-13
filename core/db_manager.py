import os
import pandas as pd
import sqlite3

def get_data_from_db():
    db_path = os.getenv('DB_PATH')
    table_name = os.getenv('TABLE_NAME', 'nuclear_safety_reports')

    if not os.path.exists(db_path):
        print(f"Базу даних не знайдено за шляхом: {db_path}")
        return None

    conn = sqlite3.connect(db_path)

    try:
        df = pd.read_sql(f'SELECT * FROM "{table_name}"', conn)
        return df
    except Exception as e:
        print(f"Помилка при читанні таблиці '{table_name}': {e}")
        return None
    finally:
        conn.close()