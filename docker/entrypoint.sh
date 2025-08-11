#!/usr/bin/env sh
set -e

# Falls SQLite genutzt wird, Zielordner aus DATABASE_URL ableiten und sicherstellen
# Beispiele:
#   sqlite:////srv/data/db/license.db  -> /srv/data/db
#   sqlite:///relative.db              -> (wird relativ zu /srv)
if printf "%s" "$DATABASE_URL" | grep -q '^sqlite:'; then
  # Strip "sqlite:" Prefix und normiere auf echten Pfad
  RAW_PATH=$(printf "%s" "$DATABASE_URL" | sed -E 's#^sqlite:/*##')
  case "$RAW_PATH" in
    /*) DB_FILE="$RAW_PATH" ;;
    *)  DB_FILE="/srv/$RAW_PATH" ;;
  esac
  DB_DIR=$(dirname "$DB_FILE")
  mkdir -p "$DB_DIR"
fi

# Schlüsselordner o.ä.
mkdir -p /srv/data/keys

exec "$@"
