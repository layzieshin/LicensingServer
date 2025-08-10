from __future__ import annotations

import base64
import json
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from cryptography.hazmat.primitives import serialization

from app.db import SessionLocal
from app.models import User, License, Activation
from app.schemas import ActivateRequest, ActivateResponse, VerifyRequest, VerifyResponse
from app.config import settings
from app.crypto import get_or_create_keypair, public_key_b64, sign_payload

router = APIRouter(prefix="/api/v1", tags=["api"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/activate", response_model=ActivateResponse)
def activate(req: ActivateRequest, db: Session = Depends(get_db)):
    """
    Enforces per-user/module seats and returns a signed activation token
    that is valid for ACTIVATION_TTL_DAYS (offline grace).
    """
    user = db.get(User, req.user_id)
    if not user or not user.active:
        return ActivateResponse(ok=False, reason="User not found or inactive")

    lic = (
        db.query(License)
        .filter(License.user_id == req.user_id, License.module_tag == req.module_tag)
        .first()
    )
    if not lic:
        return ActivateResponse(ok=False, reason="No license for module")

    # Optional expiry check (string ISO date)
    if lic.expires:
        try:
            if datetime.utcnow().date() > datetime.fromisoformat(lic.expires).date():
                return ActivateResponse(ok=False, reason="License expired")
        except Exception:
            pass  # malformed date -> ignore or deny

    # Seats enforcement: count distinct machine_ids
    distinct_machines = {a.machine_id for a in lic.activations}
    if req.machine_id not in distinct_machines and len(distinct_machines) >= lic.seats:
        return ActivateResponse(ok=False, reason="Seat limit exceeded")

    # Upsert activation for this machine
    act = (
        db.query(Activation)
        .filter(Activation.license_id == lic.id, Activation.machine_id == req.machine_id)
        .first()
    )
    now = datetime.utcnow()
    if act:
        act.last_seen_at = now
        act.app_instance_id = req.app_instance_id
    else:
        act = Activation(
            license_id=lic.id,
            machine_id=req.machine_id,
            app_instance_id=req.app_instance_id,
            created_at=now,
            last_seen_at=now,
        )
        db.add(act)
    db.commit()

    # Build signed token (payload + signature)
    priv, pub = get_or_create_keypair()
    payload = {
        "schema": 1,
        "issued_at": now.isoformat() + "Z",
        "valid_until": (now + timedelta(days=settings.ACTIVATION_TTL_DAYS)).isoformat() + "Z",
        "user_id": req.user_id,
        "module_tag": req.module_tag,
        "version": req.version,
        "machine_id": req.machine_id,
        "license": {
            "seats": lic.seats,
            "max_version": lic.max_version,
            "expires": lic.expires,
        },
    }
    payload_bytes = json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8")
    sig_b64 = sign_payload(priv, payload_bytes)

    token_obj = {
        "payload": base64.b64encode(payload_bytes).decode("ascii"),
        "signature": sig_b64,
        "alg": "Ed25519",
    }
    token = base64.b64encode(json.dumps(token_obj, separators=(",", ":")).encode("utf-8")).decode("ascii")

    return ActivateResponse(ok=True, token=token, public_key_b64=public_key_b64(pub))

@router.post("/verify", response_model=VerifyResponse)
def verify(req: VerifyRequest):
    """
    Optional server-side verification (client should verify locally as well).
    """
    try:
        token_json = base64.b64decode(req.token.encode("ascii"))
        token_obj = json.loads(token_json.decode("utf-8"))
        payload_b64 = token_obj["payload"]
        sig_b64 = token_obj["signature"]

        # Load server public key
        _, pub = get_or_create_keypair()
        pub_raw = pub.public_bytes(
            serialization.Encoding.Raw, serialization.PublicFormat.Raw
        )
        pub_key = Ed25519PublicKey.from_public_bytes(pub_raw)

        payload = base64.b64decode(payload_b64.encode("ascii"))
        signature = base64.b64decode(sig_b64.encode("ascii"))

        pub_key.verify(signature, payload)  # raises if invalid

        data = json.loads(payload.decode("utf-8"))
        # TTL check
        valid_until = datetime.fromisoformat(data["valid_until"].rstrip("Z"))
        if datetime.utcnow() > valid_until:
            return VerifyResponse(ok=False, reason="Token expired")
        return VerifyResponse(ok=True)
    except Exception as exc:
        return VerifyResponse(ok=False, reason=f"Invalid token: {exc}")
