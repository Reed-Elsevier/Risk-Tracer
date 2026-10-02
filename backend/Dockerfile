FROM python:3.12-slim

WORKDIR /app

COPY backend/pyproject.toml ./pyproject.toml
COPY backend/app ./app

RUN pip install --no-cache-dir .

COPY center_data /data

ENV DATA_DIR=/data \
    DB_PATH=/tmp/risktracer.duckdb \
    PYTHONUNBUFFERED=1

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
