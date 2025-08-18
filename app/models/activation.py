from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, DateTime, ForeignKey, Boolean
from app.core.database import Base
from app.models.base import TimestampMixin


class DeviceActivation(Base, TimestampMixin):
    __tablename__ = "device_activations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    license_id: Mapped[int] = mapped_column(ForeignKey("licenses.id", ondelete="CASCADE"), index=True)

    device_id: Mapped[str] = mapped_column(String(255), index=True)  # e.g. hashed HWID
    hostname: Mapped[str | None] = mapped_column(String(255), nullable=True)
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    last_heartbeat: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    license = relationship("License", back_populates="activations")
