from __future__ import annotations

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.db import init_db
from app.api_routes import router as api_router
from app.admin_routes import router as admin_router

init_db()
app = FastAPI(title="QMTool License Server", version="1.0")

# Routers
app.include_router(api_router)          # /api/v1/...
app.include_router(admin_router)        # / (GUI + admin actions)

# (optional) serve /static if you add assets
app.mount("/static", StaticFiles(directory="app/static"), name="static")
