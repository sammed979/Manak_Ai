#!/bin/bash
set -e

echo "==> Running database migrations..."
python -m alembic upgrade head || true

echo "==> Initializing database tables (fallback if Alembic is empty)..."
python init_db.py || true

echo "==> Seeding demo data (if enabled / DB is fresh)..."
python seed_all.py || true

echo "==> Starting Uvicorn server on 0.0.0.0:8000..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 2
