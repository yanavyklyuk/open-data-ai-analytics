import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import os

from data_load import load_data
from data_quality_analysis import prepare_data
from models import run_models_workflow

def run_visualizations(df, anomalies, feat_importance, correlations, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)

    plt.figure(figsize=(10, 6))
    plot_df = df.copy()
    plot_df['Status'] = np.where(anomalies == -1, 'Аномалія', 'Норма')
    sns.scatterplot(data=plot_df, x='irg', y='cs_137_emission', hue='Status',
                    palette={'Норма': 'blue', 'Аномалія': 'red'}, s=100, alpha=0.7)
    plt.title('Завдання 1: Виявлені аномалії (Isolation Forest)')
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.savefig(os.path.join(output_dir, '1_anomalies.png'))
    plt.close()

    plt.figure(figsize=(10, 6))
    sns.barplot(x=feat_importance.values, y=feat_importance.index, palette='viridis')
    plt.title('Завдання 2: Важливість факторів для ідентифікації АЕС')
    plt.xlabel('Важливість')
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, '2_classification_importance.png'))
    plt.close()

    corrs_to_plot = correlations.drop('index_radioactive_releas')
    plt.figure(figsize=(10, 6))
    sns.barplot(x=corrs_to_plot.values, y=corrs_to_plot.index, palette='magma')
    plt.title('Завдання 3: Вплив нуклідів на сумарний індекс безпеки')
    plt.xlabel('Коефіцієнт кореляції')
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, '3_factor_impact.png'))
    plt.close()

    print(f"Усі графіки успішно збережено у: {os.path.abspath(output_dir)}")

if __name__ == "__main__":
    path = '../data/raw/nuclear_safety_q4_2025.xlsx'
    visual_path = '../reports/figures'
    raw_data = load_data(path)

    if raw_data is not None:
        df = prepare_data(raw_data)
        anomalies, rf_model, X_test, y_test, feat_imp, corrs = run_models_workflow(df)
        print("\n--- Результати моделей ---")
        print(f"Знайдено аномалій: {len(df[anomalies == -1])}")
        run_visualizations(df, anomalies, feat_imp, corrs, visual_path)