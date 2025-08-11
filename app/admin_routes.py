"""
Admin GUI routes with session-based login.
"""

from __future__ import annotations
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Request, Form, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from app.db import session_scope
from app.models import AdminUser, License, Activation
from app.schemas import LicenseCreate
from app.security import password_context

templates = Jinja2Templates(directory="app/templates")
router = APIRouter()


# ------------------------------ helpers ------------------------------ #
def current_user(request: Request) -> Optional[str]:
    return request.session.get("user")


def require_login(request: Request) -> str:
    user = current_user(request)
    if not user:
        raise HTTPException(status_code=401)
    return user


# ------------------------------ auth ------------------------------ #
@router.get("/login", response_class=HTMLResponse)
def login_form(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@router.post("/login")
def login(request: Request, username: str = Form(...), password: str = Form(...)):
    with session_scope() as db:
        user = db.query(AdminUser).filter(AdminUser.username == username).first()
        if not user or not password_context.verify(password, user.password_hash):
            return templates.TemplateResponse(
                "login.html",
                {"request": request, "error": "Invalid credentials"},
                status_code=400,
            )
    request.session["user"] = username
    return RedirectResponse(url="/", status_code=302)


@router.get("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/login", status_code=302)


# ------------------------------ dashboard ------------------------------ #
@router.get("/", response_class=HTMLResponse)
def dashboard(request: Request, _user: str = Depends(require_login)):
    with session_scope() as db:
        lic_count = db.query(License).count()
        act_count = db.query(Activation).count()
    return templates.TemplateResponse(
        "dashboard.html",
        {"request": request, "lic_count": lic_count, "act_count": act_count},
    )


# ------------------------------ admin mgmt ------------------------------ #
@router.get("/admins", response_class=HTMLResponse)
def admins_page(request: Request, _user: str = Depends(require_login)):
    with session_scope() as db:
        admins = db.query(AdminUser).all()
    return templates.TemplateResponse(
        "admins.html", {"request": request, "admins": admins}
    )


@router.post("/admins/new")
def admins_new(request: Request, username: str = Form(...), password: str = Form(...), _user: str = Depends(require_login)):
    with session_scope() as db:
        if db.query(AdminUser).filter(AdminUser.username == username).first():
            return templates.TemplateResponse(
                "admins.html",
                {"request": request, "admins": db.query(AdminUser).all(), "error": "Username already exists."},
                status_code=400,
            )
        db.add(AdminUser(username=username, password_hash=password_context.hash(password)))
    return RedirectResponse(url="/admins", status_code=302)


@router.post("/admins/delete")
def admins_delete(request: Request, username: str = Form(...), _user: str = Depends(require_login)):
    with session_scope() as db:
        me = request.session.get("user")
        if me == username:
            return templates.TemplateResponse(
                "admins.html",
                {"request": request, "admins": db.query(AdminUser).all(), "error": "You cannot delete yourself."},
                status_code=400,
            )
        db.query(AdminUser).filter(AdminUser.username == username).delete()
    return RedirectResponse(url="/admins", status_code=302)


# ------------------------------ licenses ------------------------------ #
@router.get("/licenses", response_class=HTMLResponse)
def licenses_page(request: Request, _user: str = Depends(require_login)):
    with session_scope() as db:
        licenses = db.query(License).order_by(License.created_at.desc()).all()
    return templates.TemplateResponse(
        "licenses.html", {"request": request, "licenses": licenses}
    )


@router.post("/licenses/new")
def licenses_new(
    request: Request,
    user_name: str = Form(...),
    user_email: str = Form(...),
    module_name: str = Form(...),
    max_machines: int = Form(2),
    expires_at: str = Form(""),
    _user: str = Depends(require_login),
):
    data = LicenseCreate(
        user_name=user_name,
        user_email=user_email,
        module_name=module_name,
        max_machines=max_machines,
        expires_at=(datetime.fromisoformat(expires_at) if expires_at else None),
    )
    # Generate simple license key (you can swap in your own scheme)
    import secrets
    license_key = secrets.token_urlsafe(24)

    with session_scope() as db:
        lic = License(
            license_key=license_key,
            user_name=data.user_name,
            user_email=str(data.user_email),
            module_name=data.module_name,
            max_machines=data.max_machines,
            expires_at=data.expires_at,
        )
        db.add(lic)
    return RedirectResponse(url="/licenses", status_code=302)


@router.post("/licenses/revoke")
def licenses_revoke(license_key: str = Form(...), _user: str = Depends(require_login)):
    with session_scope() as db:
        db.query(License).filter(License.license_key == license_key).update({"revoked": True})
    return RedirectResponse(url="/licenses", status_code=302)
