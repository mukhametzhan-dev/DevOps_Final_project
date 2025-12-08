# backend/Dockerfile
FROM python:3.10-slim as builder

WORKDIR /app
# Копируем файл зависимостей
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt


COPY . /app/

# Add healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:80/health').read()" || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]
