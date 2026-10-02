#!/bin/sh
set -eu

if [ -n "${DATA_BUCKET:-}" ]; then
  python /app/fetch_s3_data.py
fi

exec uvicorn app.main:app --host 0.0.0.0 --port 8000
