"""
Database bootstrap: engine, session, Base + init_db()
"""

from __future__ import annotations
import os
from pathlib import Path
from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:////srv/data/db/license.db")


class Base(DeclarativeBase):
    """SQLAlchemy declarative base."""


# sqlite pragmas
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {},
    future=True,
)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


def _ensure_dirs() -> None:
    """Create /srv/data/db if missing."""
    if DATABASE_URL.startswith("sqlite:////"):
        db_file = DATABASE_URL.replace("sqlite:////", "/")
        Path(db_file).parent.mkdir(parents=True, exist_ok=True)


def init_db() -> None:
    """Create tables and initial admin if needed."""
    from app.models import AdminUser  # noqa: WPS433
    from app.security import password_context, ensure_keys_exist, ensure_initial_admin  # noqa: WPS433

    _ensure_dirs()
    Base.metadata.create_all(bind=engine)
    ensure_keys_exist()
    ensure_initial_admin(password_context)


@contextmanager
def session_scope():
    """Provide a transactional scope around a series of operations."""
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
