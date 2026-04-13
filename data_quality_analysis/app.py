import pandas as pd
import sqlite3
import os
import json
from dotenv import load_dotenv

load_dotenv()

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

def run_quality_analysis():
    df = get_data_from_db()

    if df is None or df.empty:
        print("Немає даних для аналізу.")
        return

    columns_info = {}
    for col in df.columns:
        columns_info[col] = {
            "type": str(df[col].dtype),
            "missing_values": int(df[col].isnull().sum())
        }

    report = {
        "total_rows": len(df),
        "total_columns": len(df.columns),
        "total_missing_values": int(df.isnull().sum().sum()),
        "duplicates": int(df.duplicated(subset=['year', 'quarter', 'station']).sum()),
        "columns_info": columns_info,
        "unique_years": sorted(df['year'].unique().tolist()),
        "unique_stations": df['station'].unique().tolist()
    }

    report_path = os.getenv('REPORTS_PATH') + 'data_quality_report.json'
    directory = os.path.dirname(report_path)

    if directory:
        os.makedirs(directory, exist_ok=True)
        print(f"Директорію '{directory}' перевірено/створено.")

    try:
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=4, ensure_ascii=False)
        print(f"Звіт успішно збережено у '{report_path}'")
    except Exception as e:
        print(f"Не вдалося записати файл: {e}")

    return report

if __name__ == "__main__":
    run_quality_analysis()