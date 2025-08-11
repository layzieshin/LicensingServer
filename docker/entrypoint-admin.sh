#!/usr/bin/env bash
set -e

: "${DATABASE_URL:=sqlite:////data/admin.db}"
: "${LOG_LEVEL:=info}"

# SQLite-Verzeichnis anlegen (nur für file-basierte URLs)
if [[ "$DATABASE_URL" == sqlite:////* ]]; then
  DB_PATH="${DATABASE_URL#sqlite:////}"
  mkdir -p "$(dirname "$DB_PATH")"
  # Datei existiert? egal – touch ist idempotent
  touch "$DB_PATH"
fi

# Start
exec uvicorn main_admin:app --host 0.0.0.0 --port 3080 --log-level "${LOG_LEVEL}"
