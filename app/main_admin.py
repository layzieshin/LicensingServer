from __future__ import annotations

import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from app.db import init_db
from app.security import ensure_initial_admin
from app.admin_routes import router as admin_router

init_db()
ensure_initial_admin()

app = FastAPI(title="Licensing Admin", version="1.0")

# sessions for login
app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv("ADMIN_SESSION_SECRET", "change-me"),
    max_age=60 * 60 * 8,  # 8h
    same_site="lax",
)

# static + templates assumed at app/static and app/templates
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# routes
app.include_router(admin_router)
