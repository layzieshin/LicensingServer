from __future__ import annotations

import os
from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware

from db import init_db
from security import ensure_initial_admin
from admin_routes import router as admin_router

app = FastAPI(title="License Admin")

# Session Secret (itsdangerous ist in den Requirements)
SECRET_KEY = os.getenv("SECRET_KEY", "please-change-me")
app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)

# DB initialisieren + Default-Admin anlegen (idempotent)
init_db()
ensure_initial_admin()

# Routen
app.include_router(admin_router)
