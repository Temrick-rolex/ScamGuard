import csv
import sys
import unicodedata
from pathlib import Path

FRAUD_MARKERS = ("arnaque", "escroquerie", "frauduleux")
LEGIT_MARKERS = ("normal", "legitime")
UNSURE_MARKERS = ("pas sur", "sais pas", "incertain")

MESSAGE_HINTS = ("copiez", "collez", "message que vous avez recu")
LABEL_HINTS = ("selon vous", "ce message est")


def simplify(value: str) -> str:
    lowered = unicodedata.normalize("NFKD", value.lower().strip())
    lowered = "".join(c for c in lowered if not unicodedata.combining(c))
    for quote in ("\u2019", "\u2018", "'", "`"):
        lowered = lowered.replace(quote, " ")
    return " ".join(lowered.split())


def read_label(value: str) -> str:
    simple = simplify(value)
    if any(marker in simple for marker in UNSURE_MARKERS):
        return "DOUTEUX"
    if any(marker in simple for marker in FRAUD_MARKERS):
        return "FRAUDE"
    if any(marker in simple for marker in LEGIT_MARKERS):
        return "LEGITIME"
    return ""


def find_column(headers: list[str], hints: tuple[str, ...]) -> str | None:
    for header in headers:
        simple = simplify(header)
        if any(hint in simple for hint in hints):
            return header
    return None


def convert(source: Path, target: Path) -> dict[str, int]:
    with source.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))

    if not rows:
        raise SystemExit("Le fichier exporte est vide")

    headers = list(rows[0].keys())
    message_column = find_column(headers, MESSAGE_HINTS)
    label_column = find_column(headers, LABEL_HINTS)

    if message_column is None or label_column is None:
        raise SystemExit(
            "Colonnes introuvables. Verifiez les intitules des questions 1 et 2.\n"
            f"Colonnes lues : {headers}"
        )

    counters = {"lus": 0, "ecrits": 0, "douteux": 0, "vides": 0}
    kept = []

    for row in rows:
        counters["lus"] += 1
        message = (row.get(message_column) or "").strip()
        label = read_label(row.get(label_column) or "")

        if len(message) < 15 or not label:
            counters["vides"] += 1
            continue
        if label == "DOUTEUX":
            counters["douteux"] += 1
            continue

        kept.append({"message": message, "etiquette": label})
        counters["ecrits"] += 1

    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["message", "etiquette"])
        writer.writeheader()
        writer.writerows(kept)

    return counters


def main() -> None:
    if len(sys.argv) < 2:
        raise SystemExit("Usage: python etl/sources/import_google_form.py <export.csv>")

    source = Path(sys.argv[1])
    target = Path("etl/sources/collecte_terrain.csv")
    counters = convert(source, target)

    print(f"Reponses lues        : {counters['lus']}")
    print(f"Retenues             : {counters['ecrits']}")
    print(f"Ecartees (douteux)   : {counters['douteux']}")
    print(f"Ecartees (invalides) : {counters['vides']}")
    print(f"Fichier ecrit        : {target}")
    print("\nEtape suivante : PYTHONPATH=. python etl/run_etl.py")


if __name__ == "__main__":
    main()
