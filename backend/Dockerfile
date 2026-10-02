FROM python:3.12-slim

WORKDIR /app

COPY backend/pyproject.toml ./pyproject.toml
COPY backend/app ./app
COPY backend/scripts/fetch_s3_data.py ./fetch_s3_data.py
COPY backend/docker-entrypoint.sh ./docker-entrypoint.sh

RUN pip install --no-cache-dir . \
    && chmod +x /app/docker-entrypoint.sh

ENV DATA_DIR=/data \
    DB_PATH=/tmp/risktracer.duckdb \
    PYTHONUNBUFFERED=1

EXPOSE 8000

ENTRYPOINT ["/app/docker-entrypoint.sh"]
