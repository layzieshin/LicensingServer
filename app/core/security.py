"""
Admin auth dependency and Ed25519 key utilities for offline tokens.
"""

from fastapi import Header, HTTPException, status
from nacl import signing, exceptions
from pathlib import Path
from app.core.config import settings

PUBLIC_KEY_FILE = "public.key"
PRIVATE_KEY_FILE = "private.key"


def verify_admin_token(x_admin_token: str | None = Header(default=None)):
    if not x_admin_token or x_admin_token != settings.ADMIN_TOKEN:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid admin token.")


def ensure_keypair_exists() -> None:
    keys_dir = Path(settings.KEYS_DIR)
    keys_dir.mkdir(parents=True, exist_ok=True)
    priv_path = keys_dir / PRIVATE_KEY_FILE
    pub_path = keys_dir / PUBLIC_KEY_FILE

    if not priv_path.exists() or not pub_path.exists():
        sk = signing.SigningKey.generate()
        vk = sk.verify_key
        priv_path.write_bytes(sk.encode())  # raw seed bytes
        pub_path.write_bytes(vk.encode())


def sign_payload(payload: bytes) -> bytes:
    sk = signing.SigningKey(Path(settings.KEYS_DIR, PRIVATE_KEY_FILE).read_bytes())
    return sk.sign(payload).signature


def verify_signature(payload: bytes, signature: bytes) -> bool:
    vk = signing.VerifyKey(Path(settings.KEYS_DIR, PUBLIC_KEY_FILE).read_bytes())
    try:
        vk.verify(payload, signature)
        return True
    except exceptions.BadSignatureError:
        return False
