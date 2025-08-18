# QMTool Licensing Server

Single-service FastAPI app that serves:
- **Admin UI** (Jinja2 templates) at `/` (protected via `X-Admin-Token`)
- **Public API** under `/api/v1` for client activation & heartbeat

## Quickstart

```bash
cp .env.example .env
# edit ADMIN_TOKEN and PORT if desired
docker compose up --build -d
# open http://localhost:8088 (or your PORT)
# send header X-Admin-Token: <your token> for UI access
