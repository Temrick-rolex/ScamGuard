from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.deps import client_ip, get_current_user, require_client
from app.db.session import get_db
from app.models import User
from app.schemas.report import (
    FeedItem,
    ReportItem,
    ReportReceipt,
    ReportRequest,
    StatsResponse,
)
from app.services import audit
from app.services.reports import history, rules, submit

router = APIRouter(prefix="/reports", tags=["Signalements"])


@router.post("", response_model=ReportReceipt, status_code=status.HTTP_201_CREATED)
def create_report(
    payload: ReportRequest,
    ip: str = Depends(client_ip),
    user: User = Depends(require_client),
    db: Session = Depends(get_db),
) -> ReportReceipt:
    try:
        report, group = submit.submit(
            db,
            user,
            payload.content,
            payload.reason,
            payload.comment,
            payload.evidence_kind,
            payload.suspect_phone,
        )
    except submit.InvalidEvidence as exc:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, str(exc)) from exc
    except submit.AlreadyReported as exc:
        raise HTTPException(status.HTTP_409_CONFLICT, str(exc)) from exc

    gaps = rules.missing_for_publication(group)
    audit.record(db, "report.create", user.id, "report", report.id, payload.reason, ip)
    db.commit()

    message = (
        "Signalement publie dans l historique."
        if group.published
        else "Signalement enregistre. Il sera visible apres verification."
    )
    return ReportReceipt(
        id=report.id,
        status=report.status,
        risk_score=report.risk_score,
        risk_level=report.risk_level,
        report_count=group.report_count,
        published=group.published,
        missing_for_publication=gaps,
        message=message,
    )


@router.get("/history", response_model=list[FeedItem])
def published_history(
    reason: str | None = None,
    limit: int = Query(default=20, le=100),
    offset: int = Query(default=0, ge=0),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[FeedItem]:
    groups = history.published_feed(db, limit, offset, reason)
    return [FeedItem.model_validate(group) for group in groups]


@router.get("/mine", response_model=list[ReportItem])
def my_reports(
    limit: int = Query(default=20, le=100),
    offset: int = Query(default=0, ge=0),
    user: User = Depends(require_client),
    db: Session = Depends(get_db),
) -> list[ReportItem]:
    return [ReportItem.model_validate(r) for r in history.my_reports(db, user.id, limit, offset)]


@router.get("/stats", response_model=StatsResponse)
def stats(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> StatsResponse:
    base = history.public_stats(db)
    return StatsResponse(**base, motifs_frequents=history.top_reasons(db))
