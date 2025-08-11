"""
Pydantic DTOs for API/Admin forms.
"""

from __future__ import annotations
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field


class LicenseCreate(BaseModel):
    user_name: str = Field(min_length=1, max_length=120)
    user_email: EmailStr
    module_name: str = Field(min_length=1, max_length=120)
    max_machines: int = Field(ge=1, le=50, default=2)
    expires_at: datetime | None = None


class LicenseVerifyRequest(BaseModel):
    license_key: str
    module_name: str
    machine_fingerprint: str


class LicenseVerifyResponse(BaseModel):
    status: str
    reason: str | None = None
    signature_b64: str | None = None
    public_key_b64: str | None = None
