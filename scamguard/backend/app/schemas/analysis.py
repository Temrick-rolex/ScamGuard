from datetime import datetime

from pydantic import BaseModel, Field


class MessageRequest(BaseModel):
    text: str = Field(min_length=5, max_length=4000)


class UrlRequest(BaseModel):
    url: str = Field(min_length=4, max_length=2000)


class EmailRequest(BaseModel):
    content: str = Field(min_length=15, max_length=20000)


class ApkRequest(BaseModel):
    app_name: str | None = Field(default=None, max_length=120)
    sha256: str | None = Field(default=None, max_length=64)
    permissions: list[str] = Field(default_factory=list, max_length=200)


class PhoneRequest(BaseModel):
    phone: str = Field(min_length=6, max_length=20)


class Explanation(BaseModel):
    code: str
    message: str


class AnalysisResponse(BaseModel):
    id: int | None = None
    score: int
    level: str
    confidence: str
    recommendation: str
    explanations: list[Explanation]
    sources: dict[str, int | None]
    extracted: dict[str, list[str]]
    model_version: str


class HistoryItem(BaseModel):
    id: int
    analysis_type: str
    risk_score: int
    risk_level: str
    confidence: str
    input_redacted: str
    created_at: datetime

    model_config = {"from_attributes": True}
