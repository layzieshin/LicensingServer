# Single Dockerfile for Admin UI + Public API
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends tini && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY app ./app
RUN mkdir -p /app/data /app/keys

# Wir exposen 3080 (intern)
EXPOSE 3080

ENTRYPOINT ["/usr/bin/tini", "--"]

# Startet uvicorn auf ${PORT} – default 3080
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-3080}"]
