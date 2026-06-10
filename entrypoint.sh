#!/bin/sh

# Exit immediately if a command exits with a non-zero status
set -e

# If we are using PostgreSQL, wait for it to be ready
if [ -n "$DATABASE_URL" ] && echo "$DATABASE_URL" | grep -q "postgresql"; then
    echo "Waiting for PostgreSQL database to be ready..."
    python -c "
import os, sys, time, socket
from urllib.parse import urlparse

db_url = os.getenv('DATABASE_URL')
if 'postgresql+asyncpg' in db_url:
    db_url = db_url.replace('postgresql+asyncpg', 'postgresql')

parsed = urlparse(db_url)
host = parsed.hostname
port = parsed.port or 5432

print(f'Checking connection to {host}:{port}...')
start_time = time.time()
while time.time() - start_time < 60:
    try:
        s = socket.create_connection((host, port), timeout=1)
        s.close()
        print('PostgreSQL is online and reachable!')
        sys.exit(0)
    except socket.error:
        time.sleep(1)
print('Timeout waiting for PostgreSQL!')
sys.exit(1)
"
fi

# Run seeding if SEED_DB environment variable is set to true
if [ "$SEED_DB" = "true" ]; then
    echo "Running database seeding..."
    python seed.py
fi

# Start uvicorn
echo "Starting FastAPI server..."
exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
