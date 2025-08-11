from __future__ import annotations

import os
from typing import Annotated, List, Dict, Any
from fastapi import APIRouter, FastAPI, Request, Form, Depends, HTTPException
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates

from app.db import session_scope
from app.models import AdminUser, License
from app.security import verify_password, get_admin_by_username, create_admin

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


def require_login(request: Request):
    if not request.session.get("admin_user"):
        raise HTTPException(status_code=401, detail="Unauthorized")
    return request.session["admin_user"]


@router.get("/", response_class=HTMLResponse)
def home(request: Request):
    if not request.session.get("admin_user"):
        # nice lightweight landing that points to /login
        return templates.TemplateResponse("welcome.html", {"request": request}, status_code=401)
    return templates.TemplateResponse("dashboard.html", {"request": request})


@router.get("/login", response_class=HTMLResponse)
def login_form(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@router.post("/login")
def login(request: Request, username: Annotated[str, Form(...)], password: Annotated[str, Form(...)]):
    with session_scope() as db:
        user = get_admin_by_username(db, username)
        if not user or not verify_password(password, user.password_hash):
            # don't leak which of both failed
            return templates.TemplateResponse("login.html", {"request": request, "error": "Invalid credentials"}, status_code=401)

        # save only minimal info in the session
        request.session["admin_user"] = {"id": user.id, "username": user.username}

    return RedirectResponse(url="/", status_code=302)


@router.get("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/login", status_code=302)


@router.get("/licenses", response_class=HTMLResponse)
def licenses_page(request: Request, _user=Depends(require_login)):
    with session_scope() as db:
        licenses = db.query(License).order_by(License.created_at.desc()).all()
        data = [
            {
                "id": l.id,
                "product": l.product,
                "customer_email": l.customer_email,
                "key": l.key,
                "valid_from": l.valid_from,
                "expires_at": l.expires_at,
                "active": l.active,
            }
            for l in licenses
        ]
    return templates.TemplateResponse("licenses.html", {"request": request, "licenses": data})


@router.get("/admins", response_class=HTMLResponse)
def admins_page(request: Request, _user=Depends(require_login)):
    with session_scope() as db:
        admins = db.query(AdminUser).order_by(AdminUser.username.asc()).all()
        data = [{"id": a.id, "username": a.username, "created_at": a.created_at} for a in admins]
    return templates.TemplateResponse("admins.html", {"request": request, "admins": data})


@router.post("/admins/create")
def admins_create(
    request: Request,
    username: Annotated[str, Form(...)],
    password: Annotated[str, Form(...)],
    _user=Depends(require_login),
):
    username = username.strip()
    if not username or len(password) < 6:
        return templates.TemplateResponse(
            "admins.html",
            {"request": request, "error": "Bitte Username angeben und Passwort min. 6 Zeichen."},
            status_code=400,
        )

    with session_scope() as db:
        if get_admin_by_username(db, username):
            return templates.TemplateResponse(
                "admins.html",
                {"request": request, "error": "User existiert bereits."},
                status_code=400,
            )
        create_admin(db, username, password)

    return RedirectResponse(url="/admins", status_code=302)
