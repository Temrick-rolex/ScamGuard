from datetime import datetime
from enum import StrEnum

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, utc_now


class AnalysisType(StrEnum):
    MESSAGE = "MESSAGE"
    URL = "URL"
    QR = "QR"
    PHONE = "PHONE"
    EMAIL = "EMAIL"
    APK = "APK"


class RiskLevel(StrEnum):
    FAIBLE = "FAIBLE"
    SUSPECT = "SUSPECT"
    DANGEREUX = "DANGEREUX"


class Analysis(Base):
    __tablename__ = "analyses"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    analysis_type: Mapped[AnalysisType] = mapped_column(String(10))
    input_redacted: Mapped[str] = mapped_column(Text)
    input_hash: Mapped[str] = mapped_column(String(64), index=True)
    risk_score: Mapped[int] = mapped_column(Integer)
    risk_level: Mapped[RiskLevel] = mapped_column(String(12), index=True)
    confidence: Mapped[str] = mapped_column(String(12), default="COMPLETE")
    explanations: Mapped[str] = mapped_column(Text, default="[]")
    model_version: Mapped[str] = mapped_column(String(20), default="absent")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, index=True)
