from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import DimLabel, FactContent

TRAINABLE_LABELS = ("FRAUDE", "LEGITIME")


def load_training_set(db: Session) -> tuple[list[str], list[int]]:
    statement = (
        select(FactContent.content_anonymise, DimLabel.label_name)
        .join(DimLabel, FactContent.label_key == DimLabel.label_key)
        .where(DimLabel.label_name.in_(TRAINABLE_LABELS))
    )

    texts: list[str] = []
    targets: list[int] = []
    for content, label in db.execute(statement):
        texts.append(content)
        targets.append(1 if label == "FRAUDE" else 0)

    return texts, targets
