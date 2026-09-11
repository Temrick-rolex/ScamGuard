from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import FactContent
from etl.load.dimensions import date_key, label_key, source_key, type_key
from etl.transform.pipeline import CleanRecord


def load_facts(db: Session, records: list[CleanRecord], run_id: int) -> tuple[int, int]:
    today = date_key(db, date.today())
    inserted = 0
    skipped = 0

    for record in records:
        exists = db.scalar(
            select(FactContent.content_key).where(FactContent.content_hash == record.content_hash)
        )
        if exists:
            skipped += 1
            continue

        db.add(
            FactContent(
                content_hash=record.content_hash,
                content_anonymise=record.content_anonymise,
                source_key=source_key(db, record.source),
                label_key=label_key(db, record.label),
                type_key=type_key(db, record.content_type),
                date_key=today,
                run_id=run_id,
                langue=record.langue,
                longueur=record.longueur,
                nb_liens=record.nb_liens,
                nb_numeros=record.nb_numeros,
            )
        )
        inserted += 1

    db.flush()
    return inserted, skipped
