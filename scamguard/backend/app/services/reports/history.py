from sqlalchemy import desc, func, select
from sqlalchemy.orm import Session

from app.models.report import Report, ReportGroup


def published_feed(
    db: Session, limit: int, offset: int, reason: str | None = None
) -> list[ReportGroup]:
    statement = select(ReportGroup).where(ReportGroup.published.is_(True))
    if reason:
        statement = statement.where(ReportGroup.main_reason == reason)

    statement = statement.order_by(desc(ReportGroup.last_seen_at)).limit(limit).offset(offset)
    return list(db.scalars(statement))


def my_reports(db: Session, user_id: int, limit: int, offset: int) -> list[Report]:
    statement = (
        select(Report)
        .where(Report.reporter_id == user_id)
        .order_by(desc(Report.created_at))
        .limit(limit)
        .offset(offset)
    )
    return list(db.scalars(statement))


def public_stats(db: Session) -> dict[str, int]:
    total = db.scalar(select(func.count()).select_from(Report)) or 0
    published = db.scalar(
        select(func.count()).select_from(ReportGroup).where(ReportGroup.published.is_(True))
    ) or 0
    phones = db.scalar(
        select(func.count(func.distinct(ReportGroup.suspect_phone))).where(
            ReportGroup.suspect_phone.is_not(None)
        )
    ) or 0
    return {
        "signalements_recus": total,
        "arnaques_publiees": published,
        "numeros_suspects": phones,
    }


def top_reasons(db: Session, limit: int = 5) -> list[dict[str, int | str]]:
    statement = (
        select(ReportGroup.main_reason, func.count().label("total"))
        .where(ReportGroup.published.is_(True))
        .group_by(ReportGroup.main_reason)
        .order_by(desc("total"))
        .limit(limit)
    )
    return [{"motif": row[0], "total": row[1]} for row in db.execute(statement)]
