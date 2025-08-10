from __future__ import annotations
from pydantic import BaseModel, Field
from typing import Optional, List

# ---- Admin DTOs ----

class UserCreate(BaseModel):
    id: str
    name: str
    email: str

class LicenseCreate(BaseModel):
    user_id: str
    module_tag: str
    max_version: Optional[str] = None
    expires: Optional[str] = None
    seats: int = Field(default=1, ge=1, le=999)

# ---- API DTOs ----

class ActivateRequest(BaseModel):
    user_id: str
    module_tag: str
    version: str
    machine_id: str
    app_instance_id: Optional[str] = None

class ActivateResponse(BaseModel):
    ok: bool
    token: Optional[str] = None
    public_key_b64: Optional[str] = None
    reason: Optional[str] = None

class VerifyRequest(BaseModel):
    token: str

class VerifyResponse(BaseModel):
    ok: bool
    reason: Optional[str] = None
