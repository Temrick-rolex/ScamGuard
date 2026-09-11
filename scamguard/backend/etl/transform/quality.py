from dataclasses import dataclass

MIN_LENGTH = 15
MAX_LENGTH = 1200


@dataclass
class Rejection:
    reason: str
    sample: str


def validate(text: str, label: str) -> Rejection | None:
    stripped = text.strip()

    if len(stripped) < MIN_LENGTH:
        return Rejection("trop_court", stripped[:60])
    if len(stripped) > MAX_LENGTH:
        return Rejection("trop_long", stripped[:60])
    if label not in {"FRAUDE", "LEGITIME", "DOUTEUX"}:
        return Rejection("etiquette_invalide", label)
    if not any(char.isalpha() for char in stripped):
        return Rejection("sans_texte", stripped[:60])

    return None


def balance_report(labels: list[str]) -> dict[str, float]:
    total = len(labels) or 1
    counts: dict[str, int] = {}
    for label in labels:
        counts[label] = counts.get(label, 0) + 1
    return {label: round(count / total, 3) for label, count in sorted(counts.items())}
