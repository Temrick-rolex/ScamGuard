from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import User
from app.models.base import utc_now
from app.models.report import Report, ReportGroup, ReportReason, ReportStatus
from app.services.reports import rules
from app.services.risk_engine.engine import analyse
from app.services.risk_engine.extractor import extract_urls, normalize_phone
from etl.transform.anonymize import anonymize
from etl.transform.normalize import content_hash


class InvalidEvidence(Exception):
    pass


class AlreadyReported(Exception):
    pass


def already_reported(db: Session, user_id: int, digest: str) -> bool:
    statement = select(func.count()).where(
        Report.reporter_id == user_id, Report.content_hash == digest
    )
    return (db.scalar(statement) or 0) > 0


def touch_group(db: Session, digest: str, redacted: str, reason: str, phone: str | None) -> ReportGroup:
    group = db.scalar(select(ReportGroup).where(ReportGroup.content_hash == digest))
    if group is None:
        group = ReportGroup(
            content_hash=digest,
            content_redacted=redacted,
            main_reason=reason,
            suspect_phone=phone,
        )
        db.add(group)
        db.flush()

    group.report_count += 1
    group.last_seen_at = utc_now()
    if phone and not group.suspect_phone:
        group.suspect_phone = phone
    return group


def submit(
    db: Session,
    user: User,
    content: str,
    reason: ReportReason,
    comment: str = "",
    evidence_kind: str = "TEXTE",
    suspect_phone: str | None = None,
) -> tuple[Report, ReportGroup]:
    if not rules.evidence_is_acceptable(evidence_kind, content):
        raise InvalidEvidence(
            "La preuve est insuffisante : collez le message complet (15 caracteres minimum)"
        )

    digest = content_hash(content)
    if already_reported(db, user.id, digest):
        raise AlreadyReported("Vous avez deja signale ce contenu")

    redacted = anonymize(content)[:2000]
    result = analyse(content)
    phone = normalize_phone(suspect_phone) if suspect_phone else None
    urls = extract_urls(content)

    report = Report(
        reporter_id=user.id,
        content_redacted=redacted,
        content_hash=digest,
        reason=reason,
        comment=comment[:500],
        evidence_kind=evidence_kind,
        suspect_phone=phone,
        suspect_url=urls[0][:500] if urls else None,
        risk_score=result.score,
        risk_level=result.level,
    )
    db.add(report)

    group = touch_group(db, digest, redacted, reason, phone)
    db.flush()
    return report, group
