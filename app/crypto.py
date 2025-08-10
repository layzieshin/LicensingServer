from __future__ import annotations

import base64
from pathlib import Path
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey, Ed25519PublicKey
)
from cryptography.hazmat.primitives import serialization

from app.config import settings


def _write_bytes(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("wb") as f:
        f.write(data)


def get_or_create_keypair() -> tuple[Ed25519PrivateKey, Ed25519PublicKey]:
    priv_path = Path(settings.PRIVATE_KEY_PATH)
    pub_path = Path(settings.PUBLIC_KEY_PATH)

    if priv_path.exists() and pub_path.exists():
        priv_bytes = priv_path.read_bytes()
        priv_key = serialization.load_pem_private_key(priv_bytes, password=None)
        pub_key = Ed25519PublicKey.from_public_bytes(
            serialization.load_pem_public_key(pub_path.read_bytes()).public_bytes(
                serialization.Encoding.Raw, serialization.PublicFormat.Raw
            )
        )
        return priv_key, pub_key

    # Create new
    priv_key = Ed25519PrivateKey.generate()
    pub_key = priv_key.public_key()

    priv_pem = priv_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )
    pub_pem = pub_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )

    _write_bytes(priv_path, priv_pem)
    _write_bytes(pub_path, pub_pem)
    return priv_key, pub_key


def public_key_b64(pub: Ed25519PublicKey) -> str:
    raw = pub.public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw)
    return base64.b64encode(raw).decode("ascii")


def sign_payload(priv: Ed25519PrivateKey, payload_bytes: bytes) -> str:
    sig = priv.sign(payload_bytes)
    return base64.b64encode(sig).decode("ascii")
