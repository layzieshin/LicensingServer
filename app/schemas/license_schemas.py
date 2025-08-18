from pydantic import BaseModel
from datetime import datetime


class LicenseCreate(BaseModel):
    user_id: int
    module_tag: str
    seats: int = 1
    max_version: str | None = None
    expires_at: datetime | None = None


class LicenseOut(BaseModel):
    id: int
    user_id: int
    module_tag: str
    seats: int
    max_version: str | None
    expires_at: datetime | None

    class Config:
        from_attributes = True
