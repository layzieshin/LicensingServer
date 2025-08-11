"""
Public API: verification + public key.
"""

from __future__ import annotations
from datetime import datetime
from fastapi import APIRouter, HTTPException
from app.db import session_scope
from app.models import License, Activation
from app.schemas import LicenseVerifyRequest, LicenseVerifyResponse
from app.security import get_public_key_b64, sign_bytes

router = APIRouter()


@router.get("/public-key", response_model=dict)
def public_key():
    return {"public_key_b64": get_public_key_b64()}


@router.post("/verify", response_model=LicenseVerifyResponse)
def verify(req: LicenseVerifyRequest) -> LicenseVerifyResponse:
    with session_scope() as db:
        lic = db.query(License).filter(
            License.license_key == req.license_key,
            License.module_name == req.module_name
        ).first()

        if not lic:
            raise HTTPException(status_code=404, detail="License not found")

        if lic.revoked:
            return LicenseVerifyResponse(status="denied", reason="revoked", public_key_b64=get_public_key_b64())

        if lic.expires_at and lic.expires_at < datetime.utcnow():
            return LicenseVerifyResponse(status="denied", reason="expired", public_key_b64=get_public_key_b64())

        act = db.query(Activation).filter(
            Activation.license_id == lic.id,
            Activation.machine_fingerprint == req.machine_fingerprint
        ).first()

        # New activation?
        if not act:
            # Count current machines
            count = db.query(Activation).filter(Activation.license_id == lic.id).count()
            if count >= lic.max_machines:
                return LicenseVerifyResponse(status="denied", reason="limit_exceeded", public_key_b64=get_public_key_b64())
            act = Activation(license_id=lic.id, machine_fingerprint=req.machine_fingerprint)
            db.add(act)
        else:
            act.last_seen = datetime.utcnow()

        payload = f"{lic.license_key}|{req.machine_fingerprint}|OK".encode("utf-8")
        sig_b64 = sign_bytes(payload)

        return LicenseVerifyResponse(
            status="ok",
            signature_b64=sig_b64,
            public_key_b64=get_public_key_b64(),
        )
