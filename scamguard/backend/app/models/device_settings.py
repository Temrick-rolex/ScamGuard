from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class DeviceSettings(Base, TimestampMixin):
    __tablename__ = "device_settings"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), unique=True)

    sms_protection: Mapped[bool] = mapped_column(Boolean, default=False)
    call_alert: Mapped[bool] = mapped_column(Boolean, default=False)
    notifications: Mapped[bool] = mapped_column(Boolean, default=True)
    last_sync_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), default=None)

    user = relationship("User", back_populates="settings")
