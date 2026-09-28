#!/usr/bin/env bash
set +e

echo "==> [1/4] Ensuring alembic/versions directory exists..."
mkdir -p alembic/versions

echo "==> [2/4] Ensuring database tables exist (idempotent)..."
python init_db.py || echo "==> WARNING: init_db.py failed (continuing anyway)"

echo "==> [3/4] Running demo data seeders (idempotent, skips if already seeded)..."
python seed_all.py || echo "==> WARNING: seed_all.py failed (ignored — server will still boot)"

echo "==> [4/4] Starting Uvicorn server on PORT=${PORT:-8000}..."
exec uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-8000}" --workers 1 --log-level info
