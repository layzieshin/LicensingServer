from __future__ import annotations

from fastapi import APIRouter, Depends, Request, Form, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.db import SessionLocal
from app.models import User, License, Activation
from app.schemas import UserCreate, LicenseCreate
from app.config import settings
from app.crypto import get_or_create_keypair, public_key_b64

router = APIRouter(tags=["admin"])
templates = Jinja2Templates(directory="app/templates")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def require_admin(request: Request):
    token = request.headers.get("Authorization", "")
    if token.startswith("Bearer "):
        token = token[7:]
    if token != settings.ADMIN_TOKEN:
        raise HTTPException(status_code=401, detail="Unauthorized")

@router.get("/")
def index(request: Request, db: Session = Depends(get_db)):
    priv, pub = get_or_create_keypair()
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "public_key_b64": public_key_b64(pub),
        },
    )

@router.get("/users")
def users(request: Request, db: Session = Depends(get_db), _: None = Depends(require_admin)):
    items = db.query(User).order_by(User.id).all()
    return templates.TemplateResponse("users.html", {"request": request, "items": items})

@router.post("/users/create")
def users_create(
    request: Request,
    id: str = Form(...),
    name: str = Form(...),
    email: str = Form(...),
    db: Session = Depends(get_db),
    _: None = Depends(require_admin),
):
    if db.get(User, id):
        raise HTTPException(status_code=400, detail="User ID exists")
    db.add(User(id=id, name=name, email=email, active=True))
    db.commit()
    return RedirectResponse(url="/users", status_code=303)

@router.post("/users/toggle")
def users_toggle(
    request: Request,
    id: str = Form(...),
    db: Session = Depends(get_db),
    _: None = Depends(require_admin),
):
    u = db.get(User, id)
    if not u:
        raise HTTPException(status_code=404, detail="Not found")
    u.active = not u.active
    db.commit()
    return RedirectResponse(url="/users", status_code=303)

@router.get("/licenses")
def licenses(request: Request, db: Session = Depends(get_db), _: None = Depends(require_admin)):
    items = (
        db.query(License)
        .order_by(License.user_id, License.module_tag)
        .all()
    )
    users = db.query(User).order_by(User.id).all()
    return templates.TemplateResponse("licenses.html", {"request": request, "items": items, "users": users})

@router.post("/licenses/create")
def licenses_create(
    request: Request,
    user_id: str = Form(...),
    module_tag: str = Form(...),
    max_version: str = Form(""),
    expires: str = Form(""),
    seats: int = Form(1),
    db: Session = Depends(get_db),
    _: None = Depends(require_admin),
):
    if not db.get(User, user_id):
        raise HTTPException(status_code=400, detail="User not found")
    lic = License(
        user_id=user_id,
        module_tag=module_tag.strip(),
        max_version=max_version.strip() or None,
        expires=expires.strip() or None,
        seats=seats,
    )
    db.add(lic)
    db.commit()
    return RedirectResponse(url="/licenses", status_code=303)

@router.post("/licenses/delete")
def licenses_delete(
    request: Request,
    id: int = Form(...),
    db: Session = Depends(get_db),
    _: None = Depends(require_admin),
):
    lic = db.get(License, id)
    if not lic:
        raise HTTPException(status_code=404, detail="Not found")
    db.delete(lic)
    db.commit()
    return RedirectResponse(url="/licenses", status_code=303)

@router.get("/activations")
def activations(request: Request, db: Session = Depends(get_db), _: None = Depends(require_admin)):
    items = (
        db.query(Activation)
        .order_by(Activation.created_at.desc())
        .limit(200)
        .all()
    )
    return templates.TemplateResponse("activations.html", {"request": request, "items": items})
