import pandas as pd
import sqlite3
import os
import json
from dotenv import load_dotenv

from core.db_manager import get_data_from_db

load_dotenv()

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