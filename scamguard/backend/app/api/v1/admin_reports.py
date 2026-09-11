from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.deps import client_ip, require_admin
from app.db.session import get_db
from app.models import User
from app.schemas.report import ModerationRequest, PendingItem, ReportItem
from app.services import audit
from app.services.reports import moderation

router = APIRouter(prefix="/admin/reports", tags=["Administration signalements"])


@router.get("/pending", response_model=list[PendingItem])
def pending(
    limit: int = Query(default=20, le=100),
    offset: int = Query(default=0, ge=0),
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
) -> list[PendingItem]:
    return [PendingItem.model_validate(r) for r in moderation.pending_queue(db, limit, offset)]


@router.post("/{report_id}/approve", response_model=ReportItem)
def approve(
    report_id: int,
    payload: ModerationRequest,
    ip: str = Depends(client_ip),
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
) -> ReportItem:
    report = _moderate(db, moderation.approve, admin, report_id, payload.note)
    audit.record(db, "report.approve", admin.id, "report", report_id, payload.note, ip)
    db.commit()
    return ReportItem.model_validate(report)


@router.post("/{report_id}/reject", response_model=ReportItem)
def reject(
    report_id: int,
    payload: ModerationRequest,
    ip: str = Depends(client_ip),
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
) -> ReportItem:
    if not payload.note.strip():
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "Un motif de rejet est requis")

    report = _moderate(db, moderation.reject, admin, report_id, payload.note)
    audit.record(db, "report.reject", admin.id, "report", report_id, payload.note, ip)
    db.commit()
    return ReportItem.model_validate(report)


def _moderate(db, action, admin, report_id, note):
    try:
        return action(db, admin, report_id, note)
    except moderation.ReportNotFound as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(exc)) from exc
    except moderation.AlreadyModerated as exc:
        raise HTTPException(status.HTTP_409_CONFLICT, str(exc)) from exc
