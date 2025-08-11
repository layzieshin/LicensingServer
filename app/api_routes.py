from __future__ import annotations

import os
from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr

from app.db import session_scope
from app.models import License, Activation

router = APIRouter(prefix="/api/v1")


class LicenseCreate(BaseModel):
    product: str
    customer_email: Optional[EmailStr] = None
    key: str
    expires_at: Optional[datetime] = None
    notes: Optional[str] = None


class LicenseVerifyRequest(BaseModel):
    product: str
    key: str
    fingerprint: str


class LicenseVerifyResponse(BaseModel):
    valid: bool
    reason: Optional[str] = None
    valid_until: Optional[datetime] = None


@router.post("/licenses")
def create_license(payload: LicenseCreate):
    with session_scope() as db:
        if db.query(License).filter(License.key == payload.key).first():
            raise HTTPException(status_code=400, detail="License key already exists")

        lic = License(
            product=payload.product,
            customer_email=payload.customer_email,
            key=payload.key,
            expires_at=payload.expires_at,
            notes=payload.notes,
        )
        db.add(lic)
        db.flush()
        return {"id": lic.id}


@router.post("/verify", response_model=LicenseVerifyResponse)
def verify(payload: LicenseVerifyRequest):
    ttl_days = int(os.getenv("ACTIVATION_TTL_DAYS", "7"))

    with session_scope() as db:
        lic = db.query(License).filter(
            License.product == payload.product,
            License.key == payload.key,
            License.active.is_(True),
        ).first()

        if not lic:
            return LicenseVerifyResponse(valid=False, reason="not_found")

        if lic.expires_at and lic.expires_at < datetime.utcnow():
            return LicenseVerifyResponse(valid=False, reason="license_expired")

        act = db.query(Activation).filter(
            Activation.license_id == lic.id,
            Activation.fingerprint == payload.fingerprint
        ).first()

        valid_until = None
        if not act:
            # first activation for this fingerprint
            act = Activation(
                license_id=lic.id,
                fingerprint=payload.fingerprint,
                valid_until=Activation.compute_default_valid_until(ttl_days),
            )
            db.add(act)
            valid_until = act.valid_until
        else:
            valid_until = act.valid_until or Activation.compute_default_valid_until(ttl_days)

        return LicenseVerifyResponse(valid=True, valid_until=valid_until)
