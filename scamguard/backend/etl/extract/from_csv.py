import csv
from pathlib import Path

from etl.transform.pipeline import RawRecord

SPAM_ALIASES = {"spam", "fraude", "fraud", "scam", "phishing", "1"}
HAM_ALIASES = {"ham", "legitime", "legit", "normal", "0"}


def read_labelled_csv(
    path: Path,
    text_column: str,
    label_column: str,
    source: str,
    content_type: str = "SMS",
    delimiter: str = ",",
) -> list[RawRecord]:
    if not path.exists():
        return []

    records: list[RawRecord] = []
    with path.open(encoding="utf-8", errors="replace", newline="") as handle:
        reader = csv.DictReader(handle, delimiter=delimiter)
        for row in reader:
            text = (row.get(text_column) or "").strip()
            raw_label = (row.get(label_column) or "").strip().lower()
            if not text:
                continue
            records.append(
                RawRecord(
                    text=text,
                    label=translate_label(raw_label),
                    source=source,
                    content_type=content_type,
                )
            )
    return records


def translate_label(raw: str) -> str:
    if raw in SPAM_ALIASES:
        return "FRAUDE"
    if raw in HAM_ALIASES:
        return "LEGITIME"
    return raw.upper()
