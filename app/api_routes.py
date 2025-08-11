from __future__ import annotations
from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends, Request
from app.db import session_scope
from app.models import License, Activation
from app.schemas import LicenseVerifyRequest, LicenseVerifyResponse
from app.security import get_public_key_b64, sign_bytes
from app.ratelimit import rate_limit
from app.audit import log_audit

router = APIRouter()

@router.get("/public-key", response_model=dict)
def public_key(request: Request, _rl=Depends(rate_limit(30, 60))):
    ip = request.client.host if request.client else "unknown"
    log_audit(actor=f"api:{ip}", action="public_key")
    return {"public_key_b64": get_public_key_b64()}

@router.post("/verify", response_model=LicenseVerifyResponse)
def verify(req: LicenseVerifyRequest, request: Request, _rl=Depends(rate_limit(60, 60))) -> LicenseVerifyResponse:
    ip = request.client.host if request.client else "unknown"
    with session_scope() as db:
        lic = db.query(License).filter(
            License.license_key == req.license_key,
            License.module_name == req.module_name
        ).first()

        if not lic:
            log_audit(actor=f"api:{ip}", action="verify_not_found", detail=req.dict())
            raise HTTPException(status_code=404, detail="License not found")

        if lic.revoked:
            log_audit(actor=f"api:{ip}", action="verify_revoked", detail={"key": lic.license_key, "fp": req.machine_fingerprint})
            return LicenseVerifyResponse(status="denied", reason="revoked", public_key_b64=get_public_key_b64())

        if lic.expires_at and lic.expires_at < datetime.utcnow():
            log_audit(actor=f"api:{ip}", action="verify_expired", detail={"key": lic.license_key, "fp": req.machine_fingerprint})
            return LicenseVerifyResponse(status="denied", reason="expired", public_key_b64=get_public_key_b64())

        act = db.query(Activation).filter(
            Activation.license_id == lic.id,
            Activation.machine_fingerprint == req.machine_fingerprint
        ).first()

        if not act:
            count = db.query(Activation).filter(Activation.license_id == lic.id).count()
            if count >= lic.max_machines:
                log_audit(actor=f"api:{ip}", action="verify_limit_exceeded", detail={"key": lic.license_key, "count": count})
                return LicenseVerifyResponse(status="denied", reason="limit_exceeded", public_key_b64=get_public_key_b64())
            act = Activation(license_id=lic.id, machine_fingerprint=req.machine_fingerprint)
            db.add(act)
        else:
            act.last_seen = datetime.utcnow()

        payload = f"{lic.license_key}|{req.machine_fingerprint}|OK".encode("utf-8")
        sig_b64 = sign_bytes(payload)
        log_audit(actor=f"api:{ip}", action="verify_ok", detail={"key": lic.license_key, "fp": req.machine_fingerprint})

        return LicenseVerifyResponse(
            status="ok",
            signature_b64=sig_b64,
            public_key_b64=get_public_key_b64(),
        )
