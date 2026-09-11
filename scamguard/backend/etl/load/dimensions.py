from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import DimDate, DimLabel, DimSource, DimType

DEFAULT_SOURCES = [
    ("datasets_publics", "externe", 3),
    ("formulaire_collecte", "terrain", 5),
    ("signalements_valides", "application", 4),
]

DEFAULT_LABELS = ["FRAUDE", "LEGITIME", "DOUTEUX"]
DEFAULT_TYPES = ["SMS", "URL", "PHONE"]


def ensure_reference_data(db: Session) -> None:
    for name, kind, reliability in DEFAULT_SOURCES:
        if not db.scalar(select(DimSource).where(DimSource.source_name == name)):
            db.add(DimSource(source_name=name, source_type=kind, reliability=reliability))

    for label in DEFAULT_LABELS:
        if not db.scalar(select(DimLabel).where(DimLabel.label_name == label)):
            db.add(DimLabel(label_name=label))

    for content_type in DEFAULT_TYPES:
        if not db.scalar(select(DimType).where(DimType.type_name == content_type)):
            db.add(DimType(type_name=content_type))

    db.flush()


def source_key(db: Session, name: str) -> int:
    row = db.scalar(select(DimSource).where(DimSource.source_name == name))
    if row is None:
        row = DimSource(source_name=name, source_type="inconnu", reliability=1)
        db.add(row)
        db.flush()
    return row.source_key


def label_key(db: Session, name: str) -> int:
    row = db.scalar(select(DimLabel).where(DimLabel.label_name == name))
    return row.label_key


def type_key(db: Session, name: str) -> int:
    row = db.scalar(select(DimType).where(DimType.type_name == name))
    return row.type_key


def date_key(db: Session, day: date) -> int:
    row = db.scalar(select(DimDate).where(DimDate.day == day))
    if row is None:
        row = DimDate(
            day=day,
            week=day.isocalendar().week,
            month=day.month,
            year=day.year,
        )
        db.add(row)
        db.flush()
    return row.date_key
