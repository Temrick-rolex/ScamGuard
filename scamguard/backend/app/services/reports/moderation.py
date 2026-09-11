from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.models import User
from app.models.base import utc_now
from app.models.report import Report, ReportGroup, ReportStatus
from app.models.reputation import PhoneReputation
from app.services.reports import rules


class ReportNotFound(Exception):
    pass


class AlreadyModerated(Exception):
    pass


def pending_queue(db: Session, limit: int, offset: int) -> list[Report]:
    statement = (
        select(Report)
        .where(Report.status == ReportStatus.EN_ATTENTE)
        .order_by(desc(Report.risk_score), Report.created_at)
        .limit(limit)
        .offset(offset)
    )
    return list(db.scalars(statement))


def load(db: Session, report_id: int) -> Report:
    report = db.get(Report, report_id)
    if report is None:
        raise ReportNotFound("Signalement introuvable")
    return report


def refresh_phone_reputation(db: Session, group: ReportGroup) -> None:
    if not group.suspect_phone:
        return

    record = db.get(PhoneReputation, group.suspect_phone)
    if record is None:
        record = PhoneReputation(phone=group.suspect_phone)
        db.add(record)

    record.report_count = group.report_count
    record.confirmed_count = group.validated_count
    record.score = rules.phone_score(group.report_count, group.validated_count)
    record.main_reason = group.main_reason
    record.last_reported_at = utc_now()


def approve(db: Session, moderator: User, report_id: int, note: str = "") -> Report:
    report = load(db, report_id)
    if report.status != ReportStatus.EN_ATTENTE:
        raise AlreadyModerated("Ce signalement a deja ete traite")

    report.status = ReportStatus.PUBLIE
    report.moderator_id = moderator.id
    report.moderation_note = note[:300]
    report.moderated_at = utc_now()

    group = db.scalar(select(ReportGroup).where(ReportGroup.content_hash == report.content_hash))
    if group is not None:
        group.validated_count += 1
        if rules.meets_publication_criteria(group):
            group.published = True
        refresh_phone_reputation(db, group)

    db.flush()
    return report


def reject(db: Session, moderator: User, report_id: int, note: str) -> Report:
    report = load(db, report_id)
    if report.status != ReportStatus.EN_ATTENTE:
        raise AlreadyModerated("Ce signalement a deja ete traite")

    report.status = ReportStatus.REJETE
    report.moderator_id = moderator.id
    report.moderation_note = note[:300]
    report.moderated_at = utc_now()
    db.flush()
    return report
