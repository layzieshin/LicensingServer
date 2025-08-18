"""
Central business logic for license validation and activations.
"""

from sqlalchemy.orm import Session
from sqlalchemy import select, func
from datetime import datetime, timedelta, timezone
from typing import Optional

from app.models.user import User
from app.models.license import License
from app.models.activation import DeviceActivation
from app.core.config import settings
from app.core.security import sign_payload
import json


def get_or_create_user(db: Session, email: str, display_name: Optional[str] = None) -> User:
    user = db.scalar(select(User).where(User.email == email))
    if user:
        return user
    user = User(email=email, display_name=display_name or email)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def find_license(db: Session, user: User, module_tag: str) -> Optional[License]:
    return db.scalar(select(License).where(License.user_id == user.id, License.module_tag == module_tag))


def seats_in_use(db: Session, lic: License) -> int:
    return db.scalar(
        select(func.count(DeviceActivation.id)).where(DeviceActivation.license_id == lic.id, DeviceActivation.active == True)  # noqa: E712
    ) or 0


def activate_device(db: Session, email: str, module_tag: str, device_id: str, hostname: Optional[str]) -> dict:
    # Ensure user & license exist
    user = db.scalar(select(User).where(User.email == email))
    if not user:
        raise ValueError("User not found")
    lic = find_license(db, user, module_tag)
    if not lic:
        raise ValueError("License not found")

    # Check expiry
    if lic.expires_at and lic.expires_at < datetime.now(timezone.utc):
        raise ValueError("License expired")

    # Enforce seats
    in_use = seats_in_use(db, lic)
    if in_use >= lic.seats:
        raise ValueError("No seats available")

    # Reuse existing activation for same device_id if exists
    act = db.scalar(select(DeviceActivation).where(DeviceActivation.license_id == lic.id, DeviceActivation.device_id == device_id))
    if act:
        if not act.active:
            act.active = True
        act.hostname = hostname or act.hostname
        act.last_heartbeat = datetime.now(timezone.utc)
        db.commit()
        db.refresh(act)
    else:
        act = DeviceActivation(
            license_id=lic.id,
            device_id=device_id,
            hostname=hostname,
            active=True,
            last_heartbeat=datetime.now(timezone.utc),
        )
        db.add(act)
        db.commit()
        db.refresh(act)

    # Create offline grace token (signed)
    payload = {
        "license_id": lic.id,
        "module_tag": lic.module_tag,
        "device_id": device_id,
        "valid_until": (datetime.now(timezone.utc) + timedelta(days=settings.OFFLINE_TOKEN_TTL_DAYS)).isoformat(),
    }
    payload_bytes = json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8")
    signature = sign_payload(payload_bytes)

    return {"activation": act, "offline_token": {"payload": payload, "signature": signature.hex()}}
