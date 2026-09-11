import json
from datetime import timedelta

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import User
from app.models.analysis import Analysis, AnalysisType
from app.models.base import utc_now
from app.services.risk_engine import reputation
from app.services.risk_engine.engine import RiskResult, analyse
from etl.transform.anonymize import anonymize
from etl.transform.normalize import content_hash

FREE_DAILY_QUOTA = 20


class QuotaExceeded(Exception):
    pass


def daily_usage(db: Session, user_id: int) -> int:
    since = utc_now() - timedelta(days=1)
    statement = select(func.count()).where(
        Analysis.user_id == user_id, Analysis.created_at >= since
    )
    return db.scalar(statement) or 0


def guard_quota(db: Session, user: User) -> None:
    if user.is_premium:
        return
    if daily_usage(db, user.id) >= FREE_DAILY_QUOTA:
        raise QuotaExceeded(
            f"Quota gratuit de {FREE_DAILY_QUOTA} analyses par jour atteint"
        )


def run_analysis(
    db: Session, user: User, text: str, analysis_type: AnalysisType
) -> tuple[RiskResult, Analysis]:
    guard_quota(db, user)

    from app.services.risk_engine.extractor import extract_urls

    verdict = reputation.lookup_urls(db, extract_urls(text))
    result = analyse(text, verdict, kind=str(analysis_type))

    record = Analysis(
        user_id=user.id,
        analysis_type=analysis_type,
        input_redacted=anonymize(text)[:2000],
        input_hash=content_hash(text),
        risk_score=result.score,
        risk_level=result.level,
        confidence=result.confidence,
        explanations=json.dumps(result.explanations, ensure_ascii=False),
        model_version=result.model_version,
    )
    db.add(record)
    db.flush()
    return result, record


def history(db: Session, user_id: int, limit: int, offset: int) -> list[Analysis]:
    statement = (
        select(Analysis)
        .where(Analysis.user_id == user_id)
        .order_by(Analysis.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    return list(db.scalars(statement))
