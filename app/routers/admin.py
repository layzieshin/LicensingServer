"""
Admin UI: token-protected minimal HTML screens to manage users, licenses and activations.
"""

from fastapi import APIRouter, Depends, Request, Form, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from sqlalchemy import select
from starlette.status import HTTP_303_SEE_OTHER

from app.core.database import get_db
from app.core.security import verify_admin_token
from app.models.user import User
from app.models.license import License
from app.models.activation import DeviceActivation
from app.schemas.license_schemas import LicenseCreate
from starlette.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/")
def admin_index(request: Request, _: None = Depends(verify_admin_token), db: Session = Depends(get_db)):
    users = db.scalars(select(User).order_by(User.id)).all()
    licenses = db.scalars(select(License).order_by(License.id)).all()
    activations = db.scalars(select(DeviceActivation).order_by(DeviceActivation.id)).all()
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "users": users, "licenses": licenses, "activations": activations},
    )


# --- Users ---

@router.post("/users/create")
def create_user(
    _: None = Depends(verify_admin_token),
    db: Session = Depends(get_db),
    email: str = Form(...),
    display_name: str = Form(...),
):
    if db.scalar(select(User).where(User.email == email)):
        raise HTTPException(status_code=400, detail="User already exists")
    u = User(email=email, display_name=display_name)
    db.add(u)
    db.commit()
    return RedirectResponse(url="/", status_code=HTTP_303_SEE_OTHER)


@router.post("/users/delete/{user_id}")
def delete_user(user_id: int, _: None = Depends(verify_admin_token), db: Session = Depends(get_db)):
    u = db.get(User, user_id)
    if u:
        db.delete(u)
        db.commit()
    return RedirectResponse(url="/", status_code=HTTP_303_SEE_OTHER)


# --- Licenses ---

@router.post("/licenses/create")
def create_license(
    _: None = Depends(verify_admin_token),
    db: Session = Depends(get_db),
    user_id: int = Form(...),
    module_tag: str = Form(...),
    seats: int = Form(1),
    max_version: str | None = Form(None),
    expires_at: str | None = Form(None),
):
    data = LicenseCreate(
        user_id=user_id,
        module_tag=module_tag.strip(),
        seats=seats,
        max_version=max_version or None,
        expires_at=(expires_at or None),
    )
    lic = License(
        user_id=data.user_id,
        module_tag=data.module_tag,
        seats=data.seats,
        max_version=data.max_version,
        expires_at=data.expires_at,
    )
    db.add(lic)
    db.commit()
    return RedirectResponse(url="/", status_code=HTTP_303_SEE_OTHER)


@router.post("/licenses/delete/{license_id}")
def delete_license(license_id: int, _: None = Depends(verify_admin_token), db: Session = Depends(get_db)):
    lic = db.get(License, license_id)
    if lic:
        db.delete(lic)
        db.commit()
    return RedirectResponse(url="/", status_code=HTTP_303_SEE_OTHER)


# --- Activations ---

@router.post("/activations/deactivate/{activation_id}")
def deactivate_activation(activation_id: int, _: None = Depends(verify_admin_token), db: Session = Depends(get_db)):
    act = db.get(DeviceActivation, activation_id)
    if act:
        act.active = False
        db.commit()
    return RedirectResponse(url="/", status_code=HTTP_303_SEE_OTHER)
