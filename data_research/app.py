import pandas as pd
import os
import json
from dotenv import load_dotenv
from sklearn.ensemble import IsolationForest, RandomForestClassifier
from sklearn.model_selection import train_test_split

from core.db_manager import get_data_from_db

load_dotenv()

def prepare_task_datasets(df):
    numeric_features = [
        'irg', 'irg_index', 'iodine_radionuclides', 'iodine_radionuclides_index',
        'stable_radionuclides', 'stable_radionuclides_index', 'cs_137_emission',
        'co_60_emission', 'cs_137_dump', 'volume'
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

def run_data_research():
    df = get_data_from_db()
    if df is None or df.empty:
        return

    desc_stats = df.describe().to_dict()
    station_analysis = df.groupby('station').mean(numeric_only=True).to_dict(orient='index')
    corr_matrix = df.corr(numeric_only=True).round(2).to_dict()

    anomalies, rf_model, X_test, y_test, feat_importance, correlations_impact = run_models_workflow(df)

    ml_results = {
        "anomalies_found": int((anomalies == -1).sum()),
        "anomaly_indices": df.index[anomalies == -1].tolist(),
        "feature_importance": feat_importance.to_dict(),
        "safety_index_impact": correlations_impact.to_dict()
    }

    research_report = {
        "descriptive_stats": desc_stats,
        "station_comparison": station_analysis,
        "correlations": corr_matrix,
        "ml_insights": ml_results
    }

    report_path = os.path.join(os.getenv('REPORTS_PATH'), 'data_research_report.json')
    os.makedirs(os.path.dirname(report_path), exist_ok=True)

    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(research_report, f, indent=4, ensure_ascii=False)

    print(f"Дослідження завершено. Результати: {report_path}")

    return df, anomalies, feat_importance, correlations_impact


if __name__ == "__main__":
    run_data_research()