"""
SQLAlchemy base classes and timestamp mixin.

This module must NOT import any concrete model classes to avoid circular imports.
"""

from __future__ import annotations

from datetime import datetime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.sql import func
from sqlalchemy import DateTime


class Base(DeclarativeBase):
    """Global declarative base for all ORM models."""
    pass


class TimestampMixin:
    """
    Adds created_at / updated_at columns with automatic timestamps.
    Safe to include in any model without extra dependencies.
    """
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        index=True,
    )
