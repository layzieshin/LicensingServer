"""
Configuration loader for environment-based settings (Pydantic v2 + pydantic-settings)
with robust parsing of CORS_ORIGINS from env (supports CSV, JSON, or "*").
"""

from functools import lru_cache
from typing import List, Any

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
import json


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
    # Accepts:
    #   - "*" (wildcard, will become ["*"])
    #   - Comma-separated list: "http://localhost:3000,https://app.example.com"
    #   - JSON list: '["http://localhost:3000","https://app.example.com"]'
    CORS_ORIGINS: List[str] = Field(default_factory=lambda: ["*"])

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore",
    )

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def _coerce_cors_origins(cls, v: Any) -> List[str]:
        if v is None or v == "":
            return ["*"]
        if isinstance(v, list):
            # already a list (e.g., from JSON)
            return [str(x).strip() for x in v if str(x).strip()]
        if isinstance(v, str):
            s = v.strip()
            if s == "*":
                return ["*"]
            # Try JSON first
            if s.startswith("["):
                try:
                    arr = json.loads(s)
                    if isinstance(arr, list):
                        return [str(x).strip() for x in arr if str(x).strip()]
                except Exception:
                    # fall through to CSV parse
                    pass
            # CSV
            return [x.strip() for x in s.split(",") if x.strip()]
        # Fallback: attempt to stringify
        return [str(v).strip()]


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
