from sqlalchemy import DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, declarative_mixin
from app.core.database import Base


@declarative_mixin
class TimestampMixin:
    created_at: Mapped["DateTime"] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped["DateTime"] = mapped_column(DateTime(timezone=True), onupdate=func.now(), nullable=True)


# Import concrete models to register with Base metadata
from app.models.user import User  # noqa
from app.models.license import License  # noqa
from app.models.activation import DeviceActivation  # noqa
