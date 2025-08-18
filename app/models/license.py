from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, DateTime, ForeignKey
from app.core.database import Base
from app.models.base import TimestampMixin


class License(Base, TimestampMixin):
    __tablename__ = "licenses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)

    module_tag: Mapped[str] = mapped_column(String(100), index=True)
    seats: Mapped[int] = mapped_column(Integer, default=1)
    max_version: Mapped[str | None] = mapped_column(String(50), nullable=True)
    expires_at: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    user = relationship("User", back_populates="licenses")
    activations = relationship("DeviceActivation", back_populates="license", cascade="all, delete-orphan")
