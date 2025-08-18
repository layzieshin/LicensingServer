# Single Dockerfile for Admin UI + Public API
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# System deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    tini && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Python deps
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# App code
COPY app ./app

# Ensure runtime folders (note: bind mounts may override these)
RUN mkdir -p /app/data /app/keys

EXPOSE 8000

# Single entry point (no split scripts)
ENTRYPOINT ["/usr/bin/tini", "--"]

# Use env PORT or default 8000
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
