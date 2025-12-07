# backend/Dockerfile
FROM python:3.10-slim as builder

WORKDIR /app
# Копируем файл зависимостей
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь код в контейнер
COPY . /app/

# CMD для запуска Uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]