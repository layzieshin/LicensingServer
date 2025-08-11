from __future__ import annotations

import os
from typing import Optional
from passlib.context import CryptContext
from sqlalchemy import select

from app.db import session_scope
from app.models import AdminUser

# bcrypt pinned via requirements to avoid 'trapped version' warning
password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return password_context.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    return password_context.verify(password, password_hash)


def get_admin_by_username(db, username: str) -> Optional[AdminUser]:
    return db.execute(select(AdminUser).where(AdminUser.username == username)).scalars().first()


def create_admin(db, username: str, password: str) -> AdminUser:
    user = AdminUser(username=username, password_hash=hash_password(password))
    db.add(user)
    db.flush()
    return user


def ensure_initial_admin() -> None:
    """Create the initial admin user if not present. Idempotent."""
    username = os.getenv("INITIAL_ADMIN_USERNAME", "admin")
    password = os.getenv("INITIAL_ADMIN_PASSWORD", "admin")

    with session_scope() as db:
        existing = get_admin_by_username(db, username)
        if existing:
            return
        create_admin(db, username, password)
