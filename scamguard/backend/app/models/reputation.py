from datetime import datetime

from sqlalchemy import DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, utc_now


class UrlReputation(Base):
    __tablename__ = "url_reputation_cache"

    url_hash: Mapped[str] = mapped_column(String(64), primary_key=True)
    verdict: Mapped[str] = mapped_column(String(20))
    score: Mapped[int] = mapped_column(Integer, default=0)
    source: Mapped[str] = mapped_column(String(30), default="interne")
    fetched_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)


class PhoneReputation(Base):
    __tablename__ = "phone_reputation"

    phone: Mapped[str] = mapped_column(String(20), primary_key=True)
    report_count: Mapped[int] = mapped_column(Integer, default=0)
    confirmed_count: Mapped[int] = mapped_column(Integer, default=0)
    score: Mapped[int] = mapped_column(Integer, default=0)
    main_reason: Mapped[str] = mapped_column(String(120), default="")
    last_reported_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
