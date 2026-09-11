from datetime import datetime

from pydantic import BaseModel, Field

from app.models.report import ReportReason


class ReportRequest(BaseModel):
    content: str = Field(min_length=15, max_length=4000)
    reason: ReportReason
    comment: str = Field(default="", max_length=500)
    evidence_kind: str = Field(default="TEXTE", max_length=20)
    suspect_phone: str | None = Field(default=None, max_length=20)


class ModerationRequest(BaseModel):
    note: str = Field(default="", max_length=300)


class ReportReceipt(BaseModel):
    id: int
    status: str
    risk_score: int
    risk_level: str
    report_count: int
    published: bool
    missing_for_publication: list[str]
    message: str


class ReportItem(BaseModel):
    id: int
    content_redacted: str
    reason: str
    status: str
    risk_score: int
    risk_level: str
    moderation_note: str
    created_at: datetime

    model_config = {"from_attributes": True}


class PendingItem(BaseModel):
    id: int
    content_redacted: str
    reason: str
    comment: str
    evidence_kind: str
    suspect_phone: str | None
    suspect_url: str | None
    risk_score: int
    risk_level: str
    created_at: datetime

    model_config = {"from_attributes": True}


class FeedItem(BaseModel):
    id: int
    content_redacted: str
    main_reason: str
    suspect_phone: str | None
    report_count: int
    validated_count: int
    last_seen_at: datetime

    model_config = {"from_attributes": True}


class StatsResponse(BaseModel):
    signalements_recus: int
    arnaques_publiees: int
    numeros_suspects: int
    motifs_frequents: list[dict[str, int | str]]
