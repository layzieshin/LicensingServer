# QMTool License Server (Minimal)

Python/FastAPI-based license server for per-user, per-module licensing with device activations.

## Features
- Users, Licenses (module_tag, seats, optional expiry/max_version)
- Device Activations with offline grace token (signed via Ed25519)
- Admin web UI (simple HTML) + API (`/api/v1`)
- Dockerized; SQLite persistence; keypair stored in volume
- Env-configurable port, admin token, DB path, token TTL

## Quickstart (Docker)
```bash
cp .env.example .env
# edit .env (ADMIN_TOKEN, PORT, etc.)
docker compose up --build -d
