"""
Database bootstrap & session management.

- Creates the SQLite database folder if missing
- Dynamically imports all model modules in app.models (except base) to register tables
- Exposes SessionLocal and get_db() dependency
"""

from __future__ import annotations

import importlib
import logging
import os
import pkgutil
from pathlib import Path
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.models.base import Base

logger = logging.getLogger(__name__)

# Ensure parent directory exists for SQLite file
db_path = Path(settings.DB_PATH)
if db_path.parent and not db_path.parent.exists():
    db_path.parent.mkdir(parents=True, exist_ok=True)

# SQLite engine (future=True uses SQLAlchemy 2.0 style)
SQLALCHEMY_DATABASE_URL = f"sqlite:///{db_path.as_posix()}"
engine = create_engine(SQLALCHEMY_DATABASE_URL, future=True)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, future=True)


def _import_all_models() -> None:
    """
    Import all modules in app.models package (except 'base') so that
    SQLAlchemy sees all mapped classes before metadata.create_all().
    This avoids circular imports by removing imports from base.py.
    """
    import app.models as models_pkg  # type: ignore

    for _, module_name, is_pkg in pkgutil.iter_modules(models_pkg.__path__):
        if is_pkg:
            continue
        if module_name == "base":
            continue
        full_name = f"{models_pkg.__name__}.{module_name}"
        try:
            importlib.import_module(full_name)
            logger.debug("Imported model module: %s", full_name)
        except Exception as exc:  # pragma: no cover
            logger.exception("Failed to import model module %s: %s", full_name, exc)
            raise


def init_db() -> None:
    """
    Initialize the database:
    - Import all models (to register mappers)
    - Create tables if they don't exist
    """
    _import_all_models()
    Base.metadata.create_all(bind=engine)
    logger.info("Database initialized at %s", db_path)


def get_db() -> Generator:
    """
    FastAPI dependency that yields a SQLAlchemy session and ensures cleanup.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
