from dataclasses import dataclass

from etl.transform.anonymize import anonymize
from etl.transform.normalize import (
    clean_text,
    content_hash,
    count_urls,
    detect_language,
    mask_urls,
)
from etl.transform.quality import Rejection, validate


@dataclass
class RawRecord:
    text: str
    label: str
    source: str
    content_type: str = "SMS"


@dataclass
class CleanRecord:
    content_hash: str
    content_anonymise: str
    label: str
    source: str
    content_type: str
    langue: str
    longueur: int
    nb_liens: int
    nb_numeros: int


def transform_one(record: RawRecord) -> CleanRecord | Rejection:
    rejection = validate(record.text, record.label)
    if rejection is not None:
        return rejection

    anonymised = anonymize(record.text)
    masked = mask_urls(anonymised)
    normalised = clean_text(masked)

    return CleanRecord(
        content_hash=content_hash(record.text),
        content_anonymise=normalised,
        label=record.label,
        source=record.source,
        content_type=record.content_type,
        langue=detect_language(record.text),
        longueur=len(record.text),
        nb_liens=count_urls(record.text),
        nb_numeros=anonymised.count("[TEL]") + anonymised.count("[NUM]"),
    )


def transform_batch(records: list[RawRecord]) -> tuple[list[CleanRecord], list[Rejection]]:
    seen: set[str] = set()
    accepted: list[CleanRecord] = []
    rejected: list[Rejection] = []

    for record in records:
        result = transform_one(record)
        if isinstance(result, Rejection):
            rejected.append(result)
            continue
        if result.content_hash in seen:
            rejected.append(Rejection("doublon", result.content_anonymise[:60]))
            continue
        seen.add(result.content_hash)
        accepted.append(result)

    return accepted, rejected
