"""
Admin FastAPI app (port 3080): session login + HTML GUI.
"""

from __future__ import annotations
import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from app.db import init_db
from app.admin_routes import router as admin_router

init_db()

app = FastAPI(title="License Admin", version="1.0")

# Session for login
app.add_middleware(SessionMiddleware, secret_key=os.getenv("SESSION_SECRET", "change-me"))

# Mount static assets
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Admin routes (HTML)
app.include_router(admin_router)
