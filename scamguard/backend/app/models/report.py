from datetime import datetime
from enum import StrEnum

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, utc_now


class ReportStatus(StrEnum):
    EN_ATTENTE = "EN_ATTENTE"
    PUBLIE = "PUBLIE"
    REJETE = "REJETE"


class ReportReason(StrEnum):
    ARNAQUE_MOBILE_MONEY = "ARNAQUE_MOBILE_MONEY"
    FAUX_GAIN = "FAUX_GAIN"
    DEMANDE_CODE = "DEMANDE_CODE"
    FRAIS_DEBLOCAGE = "FRAIS_DEBLOCAGE"
    FAUSSE_OFFRE_EMPLOI = "FAUSSE_OFFRE_EMPLOI"
    PLACEMENT_DOUTEUX = "PLACEMENT_DOUTEUX"
    USURPATION_BANQUE = "USURPATION_BANQUE"
    MENACE_CHANTAGE = "MENACE_CHANTAGE"
    AUTRE = "AUTRE"


class Report(Base):
    __tablename__ = "reports"

    id: Mapped[int] = mapped_column(primary_key=True)
    reporter_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    content_redacted: Mapped[str] = mapped_column(Text)
    content_hash: Mapped[str] = mapped_column(String(64), index=True)
    reason: Mapped[ReportReason] = mapped_column(String(30))
    comment: Mapped[str] = mapped_column(String(500), default="")
    evidence_kind: Mapped[str] = mapped_column(String(20), default="TEXTE")
    suspect_phone: Mapped[str | None] = mapped_column(String(20), index=True, default=None)
    suspect_url: Mapped[str | None] = mapped_column(String(500), default=None)
    risk_score: Mapped[int] = mapped_column(Integer, default=0)
    risk_level: Mapped[str] = mapped_column(String(12), default="FAIBLE")
    status: Mapped[ReportStatus] = mapped_column(String(12), default=ReportStatus.EN_ATTENTE, index=True)
    moderator_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), default=None)
    moderation_note: Mapped[str] = mapped_column(String(300), default="")
    moderated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), default=None)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, index=True)


class ReportGroup(Base):
    __tablename__ = "report_groups"

    id: Mapped[int] = mapped_column(primary_key=True)
    content_hash: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    content_redacted: Mapped[str] = mapped_column(Text)
    main_reason: Mapped[str] = mapped_column(String(30), default="")
    suspect_phone: Mapped[str | None] = mapped_column(String(20), index=True, default=None)
    report_count: Mapped[int] = mapped_column(Integer, default=0)
    validated_count: Mapped[int] = mapped_column(Integer, default=0)
    published: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    first_seen_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    last_seen_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, index=True)
