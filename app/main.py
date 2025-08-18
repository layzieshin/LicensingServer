"""
Main FastAPI application for QMTool Licensing Server.

- Serves Admin UI (Jinja2 templates) under '/'
- Exposes Public API under '/api/v1'
- Initializes database and key material on startup
"""

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from starlette.templating import Jinja2Templates

from app.core.config import settings
from app.core.database import init_db
from app.core.security import ensure_keypair_exists
from app.routers import admin as admin_router
from app.routers import api as api_router

app = FastAPI(title="QMTool Licensing Server", version="1.0.0")

# CORS for client apps
cors_origins = settings.CORS_ORIGINS
# Credentials dürfen nicht mit Origin="*" kombiniert werden (CORS-Spezifikation)
allow_credentials = False if cors_origins == ["*"] else True

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=allow_credentials,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files & templates
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")


@app.on_event("startup")
def on_startup() -> None:
    # Create SQLite DB and tables if not present
    init_db()
    # Ensure Ed25519 keypair exists on disk (for offline grace tokens)
    ensure_keypair_exists()


# Routers
app.include_router(admin_router.router, tags=["admin"])
app.include_router(api_router.router, prefix="/api/v1", tags=["api"])


# Health endpoint
@app.get("/health")
def health():
    return {"status": "ok"}
