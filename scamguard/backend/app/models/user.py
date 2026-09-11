from enum import StrEnum

from sqlalchemy import Boolean, Enum, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class Role(StrEnum):
    VISITOR = "VISITOR"
    CLIENT = "CLIENT"
    ADMIN = "ADMIN"


class AccountStatus(StrEnum):
    ACTIVE = "ACTIVE"
    SUSPENDED = "SUSPENDED"
    DELETED = "DELETED"


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    phone: Mapped[str | None] = mapped_column(String(20), unique=True, index=True, default=None)
    full_name: Mapped[str] = mapped_column(String(120))
    password_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[Role] = mapped_column(Enum(Role), default=Role.CLIENT)
    status: Mapped[AccountStatus] = mapped_column(Enum(AccountStatus), default=AccountStatus.ACTIVE)
    is_premium: Mapped[bool] = mapped_column(Boolean, default=False)

    settings = relationship(
        "DeviceSettings", back_populates="user", uselist=False, cascade="all, delete-orphan"
    )
    refresh_tokens = relationship(
        "RefreshToken", back_populates="user", cascade="all, delete-orphan"
    )

    @property
    def is_active(self) -> bool:
        return self.status == AccountStatus.ACTIVE
