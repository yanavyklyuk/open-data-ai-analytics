FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY data_load/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY data_load/ .

RUN mkdir -p /app/data/raw /app/db/init

CMD ["python", "app.py"]