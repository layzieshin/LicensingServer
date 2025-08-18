"""
Configuration loader for environment-based settings.
"""

from functools import lru_cache
from pydantic import BaseSettings, Field
from typing import List


class Settings(BaseSettings):
    # Server
    PORT: int = Field(8000, description="HTTP port for the service")
    ADMIN_TOKEN: str = Field("changeme-admin-token", description="Static admin token for UI access")

    # Paths (relative inside container)
    DB_PATH: str = Field("data/app.db", description="SQLite database path")
    KEYS_DIR: str = Field("keys", description="Directory for Ed25519 keypair")

    # Licensing behavior
    OFFLINE_TOKEN_TTL_DAYS: int = Field(10, description="Validity period for offline grace tokens")

    # CORS
    CORS_ORIGINS: List[str] = Field(default_factory=lambda: ["*"])

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
