FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /srv

# System deps (optional: add build-essential if needed)
RUN apt-get update && apt-get install -y --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# Python deps
RUN pip install --no-cache-dir fastapi uvicorn[standard] sqlalchemy pydantic jinja2 cryptography python-multipart

# Copy app
COPY app ./app

# Create data dirs (mounted via volume in compose)
RUN mkdir -p /srv/data/keys /srv/data/db

# Default env
ENV PORT=8080 \
    ADMIN_TOKEN=change-me-admin-token \
    DATABASE_URL=sqlite:////srv/data/db/license.db \
    ACTIVATION_TTL_DAYS=7

EXPOSE 8080

CMD ["uvicorn", "app.main:app", "--host=0.0.0.0", "--port=8080"]
