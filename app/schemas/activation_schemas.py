from pydantic import BaseModel
from datetime import datetime


class ActivationRequest(BaseModel):
    email: str
    module_tag: str
    device_id: str
    hostname: str | None = None
    client_version: str | None = None


class ActivationOut(BaseModel):
    id: int
    license_id: int
    device_id: str
    hostname: str | None
    active: bool
    last_heartbeat: datetime | None

    class Config:
        from_attributes = True


class HeartbeatRequest(BaseModel):
    device_id: str
