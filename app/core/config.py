"""
Simplified configuration loader without pydantic-settings.
Loads environment variables via python-dotenv and normalizes values.
"""

import os
from functools import lru_cache
from typing import List

from dotenv import load_dotenv
from pydantic import BaseModel, Field, field_validator

# Load .env file explicitly
load_dotenv(dotenv_path=".env")


class Settings(BaseModel):
    # ---------- Server ----------
    PORT: int = Field(8000, description="HTTP port for the service")
    ADMIN_TOKEN: str = Field("changeme-admin-token", description="Static admin token for UI access")

    # ---------- Paths ----------
    DB_PATH: str = Field("data/app.db", description="SQLite database path")
    KEYS_DIR: str = Field("keys", description="Directory for Ed25519 keypair")

    # ---------- Licensing ----------
    OFFLINE_TOKEN_TTL_DAYS: int = Field(10, description="Validity period for offline grace tokens")

    # ---------- CORS ----------
    CORS_ORIGINS: List[str] = Field(default_factory=lambda: ["*"])

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        """
        Accept:
        - "*" (wildcard)
        - CSV: "http://localhost:3000,https://app.example.com"
        - JSON-like: ["http://a","http://b"]
        """
        if v is None:
            return ["*"]
        if isinstance(v, list):
            return v
        s = str(v).strip()
        if not s:
            return ["*"]
        if s == "*":
            return ["*"]
        if s.startswith("[") and s.endswith("]"):
            s = s[1:-1]
        return [p.strip().strip('"').strip("'") for p in s.split(",") if p.strip()]


@lru_cache
def get_settings() -> Settings:
    """Load settings from environment variables."""
    return Settings(
        PORT=int(os.getenv("PORT", 8000)),
        ADMIN_TOKEN=os.getenv("ADMIN_TOKEN", "changeme-admin-token"),
        DB_PATH=os.getenv("DB_PATH", "data/app.db"),
        KEYS_DIR=os.getenv("KEYS_DIR", "keys"),
        OFFLINE_TOKEN_TTL_DAYS=int(os.getenv("OFFLINE_TOKEN_TTL_DAYS", 10)),
        CORS_ORIGINS=os.getenv("CORS_ORIGINS", "*"),
    )


settings = get_settings()
