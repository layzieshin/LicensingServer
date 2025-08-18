# Single Dockerfile for Admin UI + Public API
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# System deps für cffi / PyNaCl-Builds + tini zum sauberen Signal-Handling
RUN apt-get update && apt-get install -y --no-install-recommends \
      build-essential \
      libffi-dev \
      tini \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Python deps
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip setuptools wheel \
 && pip install --no-cache-dir -r requirements.txt

# App code
COPY app ./app
RUN mkdir -p /app/data /app/keys

# Wir exposen 3080 (intern & extern)
EXPOSE 3080

ENTRYPOINT ["/usr/bin/tini", "--"]

# Start auf Port aus env (Default 3080)
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-3080}"]
