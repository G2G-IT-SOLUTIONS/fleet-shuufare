#!/bin/sh
# FLOS Entrypoint Script
# Works on Alpine/Debian slim — CRLF-safe (dos2unix is run in Dockerfile)
set -e

# ─── Wait for PostgreSQL ────────────────────────────────────────────────────────
if [ -n "$DATABASE_URL" ] && echo "$DATABASE_URL" | grep -q "postgresql"; then
    echo "[entrypoint] Waiting for PostgreSQL to be ready..."
    python - <<'PYEOF'
import os, sys, time, socket
from urllib.parse import urlparse

db_url = os.getenv("DATABASE_URL", "")
# Strip async driver prefix if present — we only need host/port here
db_url = db_url.replace("postgresql+asyncpg", "postgresql")

parsed = urlparse(db_url)
host   = parsed.hostname or "db"
port   = parsed.port or 5432

print(f"[entrypoint] Connecting to PostgreSQL at {host}:{port} ...")
deadline = time.time() + 90  # wait up to 90 seconds
while time.time() < deadline:
    try:
        s = socket.create_connection((host, port), timeout=2)
        s.close()
        print("[entrypoint] PostgreSQL is reachable.")
        sys.exit(0)
    except socket.error:
        time.sleep(2)

print("[entrypoint] ERROR: Timed out waiting for PostgreSQL after 90 seconds.")
sys.exit(1)
PYEOF
fi

# ─── Database Schema (idempotent — safe to run on every startup) ──────────────
echo "[entrypoint] Ensuring database schema is up to date..."
python - <<'PYEOF'
from app.database import create_db_and_tables
create_db_and_tables()
print("[entrypoint] Schema OK.")
PYEOF

# ─── Optional Seed ─────────────────────────────────────────────────────────────
if [ "$SEED_DB" = "true" ]; then
    echo "[entrypoint] SEED_DB=true — Running database seed..."
    python seed.py
fi

# ─── Start Application ─────────────────────────────────────────────────────────
echo "[entrypoint] Starting FLOS (uvicorn) on port ${PORT:-8000} ..."
exec uvicorn app.main:app \
    --host 0.0.0.0 \
    --port "${PORT:-8000}" \
    --workers 1 \
    --forwarded-allow-ips "*"
