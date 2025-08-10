from __future__ import annotations
import os

class Settings:
    PORT: int = int(os.getenv("PORT", "8080"))
    ADMIN_TOKEN: str = os.getenv("ADMIN_TOKEN", "change-me-admin-token")
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:////srv/data/db/license.db")

    # Token TTL for offline grace (days)
    ACTIVATION_TTL_DAYS: int = int(os.getenv("ACTIVATION_TTL_DAYS", "7"))

    # Key storage paths (inside container volume)
    PRIVATE_KEY_PATH: str = os.getenv("PRIVATE_KEY_PATH", "/srv/data/keys/ed25519_private.key")
    PUBLIC_KEY_PATH: str = os.getenv("PUBLIC_KEY_PATH", "/srv/data/keys/ed25519_public.key")

settings = Settings()
