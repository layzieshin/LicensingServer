from __future__ import annotations

from fastapi import FastAPI

from app.db import init_db
from app.api_routes import router as api_router

init_db()
app = FastAPI(title="Licensing API", version="1.0")

# API routes (port 3445)
app.include_router(api_router)
