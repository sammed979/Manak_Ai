#!/usr/bin/env bash
set -x

echo "==> [1/4] Running database migrations (Alembic)..."
python -m alembic upgrade head || echo "==> WARNING: alembic migrations failed (ignored, will use init_db fallback)"

echo "==> [2/4] Ensuring database tables exist (init_db fallback)..."
python init_db.py || echo "==> WARNING: init_db.py failed (ignored)"

echo "==> [3/4] Running demo data seeders (idempotent, skips if already seeded)..."
python seed_all.py || echo "==> WARNING: seed_all.py failed (ignored — server will still boot)"

echo "==> [4/4] Starting Uvicorn server on PORT=${PORT:-8000}..."
exec uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-8000}" --workers 1
