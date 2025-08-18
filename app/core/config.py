"""
Configuration loader for environment-based settings (Pydantic v2 + pydantic-settings),
hardened against env parsing issues: complex values are ingested as strings first,
then normalized internally (e.g., CORS_ORIGINS).
"""

from functools import lru_cache
from typing import List

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


def _parse_cors(origins_raw: str) -> List[str]:
    """
    Accepts:
      - "*" (wildcard) -> ["*"]
      - CSV: "http://localhost:3000,https://app.example.com"
      - JSON-like list is ALSO accepted if provided by mistake, e.g. '["http://a","http://b"]'
        but parsed safely without json.loads to avoid JSON strictness at settings read time.
    """
    if origins_raw is None:
        return ["*"]
    s = (origins_raw or "").strip()
    if not s:
        return ["*"]
    if s == "*":
        return ["*"]

    # If looks like a JSON array, strip brackets and split by comma.
    # (We avoid json.loads to prevent pydantic_settings pre-decode traps.)
    if s.startswith("[") and s.endswith("]"):
        s = s[1:-1]

    parts = [p.strip().strip('"').strip("'") for p in s.split(",")]
    return [p for p in parts if p]


class Settings(BaseSettings):
    # ---------- Raw env (strings only) ----------
    # Map the env var "CORS_ORIGINS" to a raw string field to avoid JSON parsing by pydantic-settings.
    CORS_ORIGINS_RAW: str = Field("*", alias="CORS_ORIGINS")

    # ---------- Server ----------
    PORT: int = Field(8000, description="HTTP port for the service")
    ADMIN_TOKEN: str = Field("changeme-admin-token", description="Static admin token for UI access")

    # ---------- Paths ----------
    DB_PATH: str = Field("data/app.db", description="SQLite database path")
    KEYS_DIR: str = Field("keys", description="Directory for Ed25519 keypair")

    # ---------- Licensing ----------
    OFFLINE_TOKEN_TTL_DAYS: int = Field(10, description="Validity period for offline grace tokens")

    # ---------- Derived / normalized ----------
    CORS_ORIGINS: List[str] = Field(default_factory=lambda: ["*"])

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore",
        # Important: we use alias for RAW field only; derived fields stay internal.
    )

    @model_validator(mode="after")
    def _normalize(self):
        # Normalize CORS origins from the raw string
        self.CORS_ORIGINS = _parse_cors(self.CORS_ORIGINS_RAW)
        return self


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
