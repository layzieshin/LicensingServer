from __future__ import annotations
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.db import Base

class User(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True)          # e.g. "u-4711" or email
    name = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    active = Column(Boolean, default=True)

    licenses = relationship("License", back_populates="user", cascade="all, delete-orphan")

class License(Base):
    __tablename__ = "licenses"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    module_tag = Column(String, nullable=False)    # e.g., "clockwork-pro"
    max_version = Column(String, nullable=True)    # e.g., "1.x"
    expires = Column(String, nullable=True)        # ISO date string or None
    seats = Column(Integer, default=1)

    user = relationship("User", back_populates="licenses")
    activations = relationship("Activation", back_populates="license", cascade="all, delete-orphan")

class Activation(Base):
    __tablename__ = "activations"
    id = Column(Integer, primary_key=True, autoincrement=True)
    license_id = Column(Integer, ForeignKey("licenses.id"), nullable=False)
    machine_id = Column(String, nullable=False)       # hash or mac+disk hash
    app_instance_id = Column(String, nullable=True)   # optional—app session id
    created_at = Column(DateTime, default=datetime.utcnow)
    last_seen_at = Column(DateTime, default=datetime.utcnow)

    license = relationship("License", back_populates="activations")
