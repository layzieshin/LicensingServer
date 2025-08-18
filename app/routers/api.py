"""
Public API for clients: activation and heartbeat.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select
from datetime import datetime, timezone

from app.core.database import get_db
from app.schemas.activation_schemas import ActivationRequest, ActivationOut, HeartbeatRequest
from app.services.licensing_service import activate_device, get_or_create_user, find_license
from app.models.user import User
from app.models.activation import DeviceActivation

router = APIRouter()


@router.post("/activate", response_model=dict)
def api_activate(req: ActivationRequest, db: Session = Depends(get_db)):
    # Ensure user exists (self-register by email)
    user = db.scalar(select(User).where(User.email == req.email))
    if not user:
        user = get_or_create_user(db, email=req.email, display_name=req.email)

    # License must exist for the module
    result = activate_device(db, email=user.email, module_tag=req.module_tag, device_id=req.device_id, hostname=req.hostname)
    act = result["activation"]
    return {
        "activation": ActivationOut.model_validate(act).model_dump(),
        "offline_token": result["offline_token"],
    }


@router.post("/heartbeat")
def api_heartbeat(req: HeartbeatRequest, db: Session = Depends(get_db)):
    act = db.scalar(select(DeviceActivation).where(DeviceActivation.device_id == req.device_id, DeviceActivation.active == True))  # noqa: E712
    if not act:
        raise HTTPException(status_code=404, detail="Activation not found or inactive")
    act.last_heartbeat = datetime.now(timezone.utc)
    db.commit()
    return {"status": "ok"}
