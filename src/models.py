import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest, RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

from src.data_quality_analysis import prepare_data
from data_load import load_data

def prepare_task_datasets(df):
    numeric_features = [
        'irg', 'irg_index', 'iodine_ radionuclides', 'iodine_ radionuclides_index',
        'stable_radionuclides', 'stable_ radionuclides_index', 'cs_137_emission',
        'co_60_ emission', 'cs_137_dump', 'volume'
    ]

    df_anomaly = df[numeric_features].copy()

    X_class = df[numeric_features].copy()
    y_class = df['station'].copy()

    df_factors = df[numeric_features + ['index_radioactive_releas']].copy()

    return df_anomaly, X_class, y_class, df_factors

def run_models_workflow(df):
    df_anom, X_cl, y_cl, df_fact = prepare_task_datasets(df)

    iso = IsolationForest(contamination=0.05, random_state=42)
    anomalies = iso.fit_predict(df_anom)

    X_train, X_test, y_train, y_test = train_test_split(
        X_cl, y_cl, test_size=0.2, random_state=42, stratify=y_cl
    )
    rf = RandomForestClassifier(n_estimators=100, random_state=42)
    rf.fit(X_train, y_train)

    feat_importance = pd.Series(rf.feature_importances_, index=X_cl.columns).sort_values(ascending=False)

    correlations = df_fact.corr()['index_radioactive_releas'].sort_values(ascending=False)

    return anomalies, rf, X_test, y_test, feat_importance, correlations


if __name__ == "__main__":
    path = '../data/raw/nuclear_safety_q4_2025.xlsx'
    raw_data = load_data(path)

    if raw_data is not None:
        df = prepare_data(raw_data)
        results = run_models_workflow(df)
        print(results)