from __future__ import annotations

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from sqlalchemy import select

from db import session_scope
from models import AdminUser
from templating import templates  # statt: from templates import templates

router = APIRouter()


@router.get("/admins", response_class=HTMLResponse)
def admins_page(request: Request):
    """
    DetachedInstanceError fix:
    Datensätze werden innerhalb der Session in primitive Dicts konvertiert,
    bevor die Session geschlossen wird.
    """
    with session_scope() as db:
        rows = db.execute(select(AdminUser).order_by(AdminUser.username)).scalars().all()
        admins = [{"id": a.id, "username": a.username} for a in rows]

    return templates.TemplateResponse(
        "admins.html",
        {"request": request, "admins": admins},
    )
