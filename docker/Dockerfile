# docker/Dockerfile
# Single Dockerfile for both Admin UI and Public API
FROM python:3.12-slim

# System deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential tini && \
    rm -rf /var/lib/apt/lists/*

# Workdir
WORKDIR /app

# Python deps
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# App code
COPY app ./app

# Ensure runtime folders
RUN mkdir -p data keys

# Non-root
RUN useradd -ms /bin/bash appuser
USER appuser

EXPOSE 8000

# Single entry point (no split scripts)
ENTRYPOINT ["/usr/bin/tini", "--"]

# Use env PORT or default 8000
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
