from __future__ import annotations
from typing import Mapping
from json import dumps
from app.db import session_scope
from app.models import AuditLog

def log_audit(actor: str, action: str, detail: Mapping | str | None = None) -> None:
    if not detail:
        detail_txt = ""
    elif isinstance(detail, str):
        detail_txt = detail
    else:
        detail_txt = dumps(detail, ensure_ascii=False)
    with session_scope() as db:
        db.add(AuditLog(actor=actor[:120], action=action[:80], detail=detail_txt[:2000]))
