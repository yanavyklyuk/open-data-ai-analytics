import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import os

from dotenv import load_dotenv

from data_research.app import run_data_research

load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, "..", ".env"))

def run_visualizations():
    result = run_data_research()
    if result is None:
        print("Не вдалося отримати дані для візуалізації.")
        return

    df, anomalies, feat_imp, corrs = result

    FIGURES_DIR = os.getenv("FIGURES_DIR")
    os.makedirs(FIGURES_DIR, exist_ok=True)

    plt.figure(figsize=(10, 6))
    plot_df = df.copy()
    plot_df['Status'] = np.where(anomalies == -1, 'Аномалія', 'Норма')
    sns.scatterplot(data=plot_df, x='irg', y='cs_137_emission', hue='Status',
                    palette={'Норма': 'blue', 'Аномалія': 'red'}, s=100, alpha=0.7)
    plt.title('Завдання 1: Виявлені аномалії (Isolation Forest)')
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.savefig(os.path.join(FIGURES_DIR, '1_anomalies.png'))
    plt.close()

    plt.figure(figsize=(10, 6))
    sns.barplot(x=feat_imp.values, y=feat_imp.index, palette='viridis')
    plt.title('Завдання 2: Важливість факторів для ідентифікації АЕС')
    plt.xlabel('Важливість')
    plt.tight_layout()
    plt.savefig(os.path.join(FIGURES_DIR, '2_classification_importance.png'))
    plt.close()

    corrs_to_plot = corrs.drop('index_radioactive_releas')
    plt.figure(figsize=(10, 6))
    sns.barplot(x=corrs_to_plot.values, y=corrs_to_plot.index, palette='magma')
    plt.title('Завдання 3: Вплив нуклідів на сумарний індекс безпеки')
    plt.xlabel('Коефіцієнт кореляції')
    plt.tight_layout()
    plt.savefig(os.path.join(FIGURES_DIR, '3_factor_impact.png'))
    plt.close()

    print(f"Усі графіки успішно збережено у: {os.path.abspath(FIGURES_DIR)}")

if __name__ == "__main__":
    run_visualizations()