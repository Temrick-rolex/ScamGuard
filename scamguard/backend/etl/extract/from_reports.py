from sqlalchemy import select
from sqlalchemy.orm import Session

from etl.transform.pipeline import RawRecord

SOURCE_NAME = "signalements_valides"


def read_validated_reports(db: Session) -> list[RawRecord]:
    try:
        from app.models.report import Report, ReportStatus
    except ImportError:
        return []

    statement = select(Report).where(Report.status == ReportStatus.ACCEPTED)
    return [
        RawRecord(
            text=report.content,
            label="FRAUDE",
            source=SOURCE_NAME,
            content_type=report.content_type,
        )
        for report in db.scalars(statement)
        if report.content
    ]
