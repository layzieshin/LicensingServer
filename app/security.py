from __future__ import annotations

import os
from typing import Optional

from passlib.context import CryptContext
from sqlalchemy import select

from db import session_scope
from models import AdminUser

# Passlib-Kontext – bcrypt ist per requirements auf 4.0.1 gepinnt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, password_hash: str) -> bool:
    return pwd_context.verify(plain_password, password_hash)


def hash_password(plain_password: str) -> str:
    return pwd_context.hash(plain_password)


def ensure_initial_admin(context: Optional[CryptContext] = None) -> None:
    """
    Idempotent: legt einen 'admin' an, wenn keiner existiert.
    Nutzt ENV ADMIN_USERNAME / ADMIN_PASSWORD (Fallback 'admin'/'admin').
    """
    ctx = context or pwd_context
    default_user = os.getenv("ADMIN_USERNAME", "admin")
    default_pass = os.getenv("ADMIN_PASSWORD", "admin")

    with session_scope() as db:
        exists = db.execute(
            select(AdminUser).where(AdminUser.username == default_user)
        ).scalar_one_or_none()

        if exists:
            return

        user = AdminUser(username=default_user, password_hash=ctx.hash(default_pass))
        db.add(user)
        # commit folgt im session_scope() nur, wenn es Änderungen gab
