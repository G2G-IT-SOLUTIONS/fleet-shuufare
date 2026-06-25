# ─────────────────────────────────────────────
#  FLOS — Fleet Operations System
#  Multi-stage Dockerfile (Windows Server compatible)
# ─────────────────────────────────────────────

FROM python:3.11-slim AS base

# Prevent .pyc files and enable unbuffered stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000 \
    # Ensure pip does not write to root-owned cache inside the container
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# ─── System Dependencies ───────────────────────────────────────────────────────
# build-essential  → compiles psycopg2 / bcrypt C extensions
# libpq-dev        → PostgreSQL client headers needed by psycopg2
# curl             → healthcheck probe
# dos2unix         → normalises CRLF line endings in entrypoint.sh (Windows dev)
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        libpq-dev \
        curl \
        dos2unix \
    && rm -rf /var/lib/apt/lists/*

# ─── Python Dependencies ───────────────────────────────────────────────────────
# Copy requirements first to leverage Docker layer cache.
# Rebuilds only when requirements.txt changes, not on every code change.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ─── Application Code ──────────────────────────────────────────────────────────
COPY . .

# Normalise line endings on entrypoint (handles Windows CRLF → LF)
RUN dos2unix entrypoint.sh && chmod +x entrypoint.sh

# ─── Non-root User (security best practice) ───────────────────────────────────
RUN addgroup --system flos && adduser --system --ingroup flos flos
RUN chown -R flos:flos /app
USER flos

# ─── Runtime ───────────────────────────────────────────────────────────────────
EXPOSE 8000

# Docker health check — polls the FastAPI /docs endpoint (lightweight, always available)
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/docs || exit 1

ENTRYPOINT ["/app/entrypoint.sh"]
