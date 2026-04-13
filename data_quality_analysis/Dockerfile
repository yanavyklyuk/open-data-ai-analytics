FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY data_quality_analysis/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY core/ ./core/

COPY data_quality_analysis/ .

RUN mkdir -p /app/reports/files

CMD ["python", "app.py"]