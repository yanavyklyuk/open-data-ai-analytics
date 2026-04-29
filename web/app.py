import streamlit as st
import json
import os
import pandas as pd
from PIL import Image

from dotenv import load_dotenv
from prometheus_client import start_http_server, Counter, Gauge

PAGE_VIEWS = Counter('app_page_views_total', 'Загальна кількість переглядів сторінок', ['page_name'])
ANOMALIES_GAUGE = Gauge('app_detected_anomalies_count', 'Кількість виявлених аномалій у звіті')

load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

load_dotenv(os.path.join(BASE_DIR, "..", ".env"))

raw_reports_path = os.getenv('REPORTS_PATH', '../reports/files/').strip()
raw_figures_path = os.getenv('FIGURES_DIR', '../reports/figures/').strip()

REPORTS_PATH = os.path.abspath(os.path.join(BASE_DIR, raw_reports_path))
FIGURES_PATH = os.path.abspath(os.path.join(BASE_DIR, raw_figures_path))

def load_json(filename):
    path = os.path.join(REPORTS_PATH, filename)
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None

def main():
    try:
        start_http_server(8000)
    except:
        pass

    st.set_page_config(page_title="Моніторинг АЕС", layout="wide")

    st.sidebar.title("Навігація")
    page = st.sidebar.radio("Оберіть розділ:",
                            ["Головна", "Аналіз якості даних", "Результати дослідження", "Візуалізація"])

    PAGE_VIEWS.labels(page_name=page).inc()

    if page == "Головна":
        st.title("🛡️ Аналіз екологічної обстановки АЕС України")

        st.markdown(f"""
            ### 🎯 Мета проєкту
            Дослідити динаміку радіоактивних викидів та скидів українських атомних електростанцій (2018–2025), 
            виявити приховані закономірності та побудувати ML-моделі для аналізу екологічного стану.

            ### 🔍 Ключові гіпотези аналізу:
            1. **Пошук аномалій:** Виявлення кварталів з нетипово високим рівнем викидів, що можуть свідчити про технічні особливості експлуатації.
            2. **«Цифровий відбиток» станцій:** Перевірка можливості ідентифікації конкретної АЕС за унікальним профілем нуклідів.
            3. **Факторний аналіз:** Визначення домінуючих факторів, що мають критичний вплив на сумарний індекс безпеки.

            ### 📊 Джерело даних
            Дані отримані з **Єдиного державного порталу відкритих даних**.
            """)

        st.info("Проєкт реалізовано з використанням Python (Pandas, Scikit-learn) та методів Machine Learning.")

    elif page == "Аналіз якості даних":
        st.title("📊 Перевірка якості даних")
        report = load_json('data_quality_report.json')

        if report:
            ANOMALIES_GAUGE.set(report.get('duplicates', 0))
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Загалом записів", report['total_rows'])
            col2.metric("Загалом ознак", report['total_columns'])
            col3.metric("Кількість дублікатів", report['duplicates'])
            col4.metric("Кількість пропущених значень", report['total_missing_values'])

            st.divider()

            c1, c2 = st.columns(2)
            with c1:
                st.subheader("🗓️ Аналізовані роки")
                st.write(", ".join(map(str, report['unique_years'])))
            with c2:
                st.subheader("🏢 Станції")
                st.write(", ".join(report['unique_stations']))

            st.subheader("Інформація про колонки")
            st.dataframe(pd.DataFrame(report['columns_info']).T, use_container_width=True)
        else:
            st.error("Звіт про якість даних не знайдено.")

    elif page == "Результати дослідження":
        st.title("🧠 Дослідження та Статистика")

        research = load_json('data_research_report.json')

        if research:
            with st.expander("📊 Повна описова статистика (натисніть, щоб розгорнути)"):
                stats_df = pd.DataFrame(research['descriptive_stats']).T
                st.dataframe(stats_df, use_container_width=True)

            st.divider()

            st.subheader("🏢 Порівняння станцій за середнім значенням обраного показника")
            comp_df = pd.DataFrame(research['station_comparison']).T

            metrics = [c for c in comp_df.columns if c not in ['year', 'quarter']]
            selected_metric = st.selectbox("Оберіть показник для порівняння:", metrics)
            st.bar_chart(comp_df[selected_metric])

            st.divider()

            st.subheader("🔗 Матриця кореляції між показниками")
            corr_df = pd.DataFrame(research['correlations'])

            st.dataframe(corr_df.style.background_gradient(cmap='RdBu_r', axis=None).format("{:.2f}"), use_container_width=True)
            st.divider()

            ml = research.get('ml_insights', {})
            st.subheader("🔍 Результати ML дослідження")
            c1, c2 = st.columns([1, 2])

            with c1:
                st.metric("Виявлено аномалій", ml.get('anomalies_found', 0))
                st.write("**Вплив показників на формування загального індексу викидів (коефіцієнт кореляції):**")
                st.json(ml.get('safety_index_impact', {}))

            with c2:
                st.write("**Важливість факторів (Feature Importance):**")
                feat_imp = pd.Series(ml.get('feature_importance', {}))
                st.bar_chart(feat_imp)

        else:

            st.error("Звіт дослідження не знайдено.")

    elif page == "Візуалізація":
        st.title("📈 Візуалізація результатів")
        images = {
            "1_anomalies.png": "Виявлені аномалії (Isolation Forest)",
            "2_classification_importance.png": "Важливість факторів для ідентифікації АЕС",
            "3_factor_impact.png": "Вплив нуклідів на загальну безпеку"
        }

        for file, desc in images.items():
            img_path = os.path.join(FIGURES_PATH, file)
            if os.path.exists(img_path):
                st.subheader(desc)
                st.image(Image.open(img_path))
            else:
                st.info(f"Очікується файл: {file}")


if __name__ == "__main__":
    main()