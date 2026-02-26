import pandas as pd
import numpy as np

from data_load import load_data

def check_data_quality(df):
    dirty_cols = [col for col in df.columns if col != col.strip()]
    if dirty_cols:
        print(f"Виявлено назви колонок з пробілами: {dirty_cols}")

    null_counts = df.isnull().sum()
    if null_counts.sum() > 0:
        print("\nВиявлено пропуски (NaN):")
        print(null_counts[null_counts > 0])
    else:
        print("\nПропусків не виявлено.")

    stations = df['station'].unique()
    print(f"\nСтанції в датасеті: {stations}")
    if 'ЮУАЕС' in stations and 'ПАЕС' in stations:
        print("Увага: Одна і та сама станція записана двома іменами (ЮУАЕС та ПАЕС).")

    sample_cols = ['iodine_ radionuclides_index', 'stable_ radionuclides_index', 'index_dump']
    print("\nПеревірка на наявність '<0,01':")
    for col in sample_cols:
        if col in df.columns:
            has_less_than = df[col].astype(str).str.contains('<').any()
            print(f"- Колонку '{col}' треба конвертувати: {has_less_than}")

def prepare_data(df):
    df.columns = df.columns.str.strip()
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

    print(f"Дані перевірено та підготовлено! Залишилось рядків: {len(df)}, колонок: {len(df.columns)}")
    return df


if __name__ == "__main__":
    path = '../data/raw/nuclear_safety_q4_2025.xlsx'
    raw_data = load_data(path)

    if raw_data is not None:
        check_data_quality(raw_data)
        df_final = prepare_data(raw_data)