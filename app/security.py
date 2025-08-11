"""
Security utils:
- Password hashing (bcrypt via passlib)
- Session secret
- Ed25519 keypair for signing verification responses
- Initial admin bootstrap
"""

from __future__ import annotations
import os
from base64 import b64encode
from pathlib import Path
from typing import Tuple

from passlib.context import CryptContext
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.serialization import (
    Encoding, PrivateFormat, NoEncryption, PublicFormat
)

from app.db import session_scope
from app.models import AdminUser

password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

KEYS_DIR = Path("/srv/data/keys")
PRIVATE_KEY_FILE = KEYS_DIR / "ed25519_private.pem"
PUBLIC_KEY_FILE = KEYS_DIR / "ed25519_public.pem"


def ensure_keys_exist() -> None:
    """Generate Ed25519 key pair if files are missing."""
    KEYS_DIR.mkdir(parents=True, exist_ok=True)
    if not PRIVATE_KEY_FILE.exists() or not PUBLIC_KEY_FILE.exists():
        priv = Ed25519PrivateKey.generate()
        pub = priv.public_key()

        PRIVATE_KEY_FILE.write_bytes(
            priv.private_bytes(Encoding.PEM, PrivateFormat.PKCS8, NoEncryption())
        )
        PUBLIC_KEY_FILE.write_bytes(
            pub.public_bytes(Encoding.Raw, PublicFormat.Raw)
        )


def load_private_key() -> Ed25519PrivateKey:
    data = PRIVATE_KEY_FILE.read_bytes()
    return Ed25519PrivateKey.from_private_bytes(
        # Extract raw key from PEM if necessary:
        Ed25519PrivateKey.from_private_bytes.__self__.from_private_bytes  # type: ignore[attr-defined]
        if False else _pem_to_raw_private(data)  # noqa: E712
    )


def _pem_to_raw_private(pem: bytes) -> bytes:
    """Parse PKCS8 PEM to raw 32 bytes."""
    # cryptography can load PEM directly:
    from cryptography.hazmat.primitives import serialization
    key = serialization.load_pem_private_key(pem, password=None)
    raw = key.private_bytes(Encoding.Raw, PrivateFormat.Raw, NoEncryption())
    return raw


def get_public_key_b64() -> str:
    if not PUBLIC_KEY_FILE.exists():
        ensure_keys_exist()
    raw = PUBLIC_KEY_FILE.read_bytes()
    return b64encode(raw).decode("ascii")


def sign_bytes(message: bytes) -> str:
    """Sign payload with Ed25519 private key and return base64 signature."""
    from cryptography.hazmat.primitives import serialization
    priv = serialization.load_pem_private_key(PRIVATE_KEY_FILE.read_bytes(), password=None)
    sig = priv.sign(message)
    return b64encode(sig).decode("ascii")


def ensure_initial_admin(pwd_ctx: CryptContext) -> None:
    """Create initial admin from env if table empty."""
    user = os.getenv("INITIAL_ADMIN_USER", "admin")
    pwd = os.getenv("INITIAL_ADMIN_PASSWORD", "ChangeMe123!")
    with session_scope() as db:
        exists = db.query(AdminUser).count()
        if exists == 0:
            db.add(AdminUser(username=user, password_hash=pwd_ctx.hash(pwd)))
