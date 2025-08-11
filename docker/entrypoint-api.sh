#!/usr/bin/env bash
set -e

: "${DATABASE_URL:=sqlite:////data/api.db}"
: "${LOG_LEVEL:=info}"

if [[ "$DATABASE_URL" == sqlite:////* ]]; then
  DB_PATH="${DATABASE_URL#sqlite:////}"
  mkdir -p "$(dirname "$DB_PATH")"
  touch "$DB_PATH"
fi

exec uvicorn main_api:app --host 0.0.0.0 --port 3445 --log-level "${LOG_LEVEL}"
