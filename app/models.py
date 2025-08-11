"""
SQLAlchemy models: AdminUser, License, Activation
"""

from __future__ import annotations
from datetime import datetime
from sqlalchemy import String, Integer, DateTime, Boolean, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class AdminUser(Base):
    __tablename__ = "admin_users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(80), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))


class License(Base):
    __tablename__ = "licenses"

    id: Mapped[int] = mapped_column(primary_key=True)
    license_key: Mapped[str] = mapped_column(String(128), unique=True, index=True)

    # who / what
    user_name: Mapped[str] = mapped_column(String(120))
    user_email: Mapped[str] = mapped_column(String(200))
    module_name: Mapped[str] = mapped_column(String(120), index=True)

    # policy
    max_machines: Mapped[int] = mapped_column(Integer, default=2)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    revoked: Mapped[bool] = mapped_column(Boolean, default=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    activations: Mapped[list["Activation"]] = relationship(
        back_populates="license", cascade="all, delete-orphan"
    )


class Activation(Base):
    __tablename__ = "activations"
    __table_args__ = (
        UniqueConstraint("license_id", "machine_fingerprint", name="uq_license_machine"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    license_id: Mapped[int] = mapped_column(ForeignKey("licenses.id", ondelete="CASCADE"), index=True)
    machine_fingerprint: Mapped[str] = mapped_column(String(64), index=True)
    activated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    last_seen: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    license: Mapped["License"] = relationship(back_populates="activations")
