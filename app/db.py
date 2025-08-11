from __future__ import annotations

import os
from contextlib import contextmanager
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker, Session

# WICHTIG:
# - Base & Modelle werden aus models importiert (so wie bisher genutzt)
# - init_db() ruft create_all auf der importierten Base auf
try:
    from models import Base  # gleiche Struktur wie im Repo beibehalten
except Exception as exc:  # pragma: no cover
    raise RuntimeError("Konnte models.Base nicht importieren") from exc


def _default_sqlite_url() -> str:
    role = os.getenv("APP_ROLE", "app").strip().lower()
    filename = "admin.db" if role == "admin" else ("api.db" if role == "api" else "app.db")
    return f"sqlite:////data/{filename}"


def _make_engine() -> Engine:
    url = os.getenv("DATABASE_URL", "").strip() or _default_sqlite_url()

    connect_args = {}
    if url.startswith("sqlite:"):
        # Verzeichnis vor dem Verbinden anlegen
        path = url.replace("sqlite:////", "/")
        os.makedirs(os.path.dirname(path), exist_ok=True)
        connect_args["check_same_thread"] = False

    return create_engine(
        url,
        connect_args=connect_args,
        pool_pre_ping=True,
        future=True,
    )


ENGINE: Engine = _make_engine()
SessionLocal = sessionmaker(bind=ENGINE, autoflush=False, autocommit=False, future=True)


def init_db() -> None:
    """Erzeugt Tabellen, falls sie fehlen."""
    Base.metadata.create_all(bind=ENGINE)


@contextmanager
def session_scope() -> Generator[Session, None, None]:
    """Contextmanager für Sessions: commit/rollback/close sicher handhaben."""
    db: Session = SessionLocal()
    try:
        yield db
        # Nur committen, wenn Änderungen passiert sind
        if db.new or db.dirty or db.deleted:
            db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
