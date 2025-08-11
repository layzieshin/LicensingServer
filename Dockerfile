FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /srv

# System deps (minimal)
RUN apt-get update && apt-get install -y --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# Python deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app
COPY app ./app

# Ensure data dirs (will also be mounted by compose)
RUN mkdir -p /srv/data/keys /srv/data/db

# Default env (can be overridden by .env / compose)
ENV PORT_ADMIN=3080 \
    PORT_API=3445 \
    DATABASE_URL=sqlite:////srv/data/db/license.db \
    SESSION_SECRET=change-me-session-secret \
    INITIAL_ADMIN_USER=admin \
    INITIAL_ADMIN_PASSWORD=ChangeMe123! \
    LICENSE_DEFAULT_MAX_MACHINES=2

EXPOSE 3080 3445

# Default command runs the admin app; API container overrides via compose
CMD ["uvicorn", "app.main_admin:app", "--host=0.0.0.0", "--port=3080"]
