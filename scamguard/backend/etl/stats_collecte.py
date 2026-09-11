import sys
from collections import Counter
from pathlib import Path

from etl.sources.import_google_form import find_column, read_label

QUESTIONS = {
    "type": ("de quel type", "quel type"),
    "canal": ("par quel canal", "canal"),
    "lien": ("contenait-il un lien", "un lien"),
    "perte": ("perdu de l argent", "perdu"),
    "region": ("quelle region", "region"),
    "etiquette": ("selon vous", "ce message est"),
}

CIBLE = 400


def bar(value: int, total: int, width: int = 32) -> str:
    if total == 0:
        return ""
    filled = round(width * value / total)
    return "#" * filled + "." * (width - filled)


def section(title: str, counter: Counter, total: int) -> None:
    if not counter:
        return
    print(f"\n{title}")
    print("-" * 62)
    for label, count in counter.most_common():
        share = 100 * count / total if total else 0
        print(f"  {label[:30]:<30} {count:>4}  {share:>5.1f}%  {bar(count, total, 18)}")


def main() -> None:
    import csv

    if len(sys.argv) < 2:
        raise SystemExit("Usage: PYTHONPATH=. python etl/stats_collecte.py <export.csv>")

    with Path(sys.argv[1]).open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))

    if not rows:
        raise SystemExit("Fichier vide")

    headers = list(rows[0].keys())
    columns = {key: find_column(headers, hints) for key, hints in QUESTIONS.items()}
    total = len(rows)

    print("=" * 62)
    print("  STATISTIQUES DE COLLECTE - ScamGuard")
    print("=" * 62)
    print(f"\nReponses recues : {total}   Objectif : {CIBLE}")
    print(f"Progression     : {bar(min(total, CIBLE), CIBLE)}  {100 * total / CIBLE:.0f}%")

    counters = {key: Counter() for key in QUESTIONS}
    for row in rows:
        for key, column in columns.items():
            if column:
                value = (row.get(column) or "").strip()
                counters[key][value or "(non renseigne)"] += 1

    labels = counters["etiquette"]
    fraude = sum(v for k, v in labels.items() if read_label(k) == "FRAUDE")
    legitime = sum(v for k, v in labels.items() if read_label(k) == "LEGITIME")
    douteux = total - fraude - legitime
    utilisables = fraude + legitime

    print(f"\nEQUILIBRE DU JEU DE DONNEES")
    print("-" * 62)
    print(f"  Arnaques           {fraude:>4}  {100 * fraude / total:>5.1f}%  {bar(fraude, total, 18)}")
    print(f"  Messages normaux   {legitime:>4}  {100 * legitime / total:>5.1f}%  {bar(legitime, total, 18)}")
    print(f"  Douteux (exclus)   {douteux:>4}  {100 * douteux / total:>5.1f}%  {bar(douteux, total, 18)}")
    print(f"\n  Utilisables pour l entrainement : {utilisables}")

    section("TYPES D ARNAQUE", counters["type"], total)
    section("CANAL DE RECEPTION", counters["canal"], total)
    section("PRESENCE D UN LIEN", counters["lien"], total)
    section("IMPACT SUBI", counters["perte"], total)
    section("REPARTITION GEOGRAPHIQUE", counters["region"], total)

    print("\n" + "=" * 62)
    print("  DIAGNOSTIC")
    print("=" * 62)

    alerts = []
    if utilisables < 200:
        alerts.append(f"Volume insuffisant ({utilisables}). Minimum vital : 200.")
    if legitime and fraude / legitime > 2.5:
        alerts.append("Trop d arnaques. Relancez sur les messages NORMAUX.")
    if fraude and legitime / fraude > 2.0:
        alerts.append("Trop de messages normaux. Relancez sur les arnaques.")
    if douteux > total * 0.25:
        alerts.append("Beaucoup de douteux : la question 2 est mal comprise.")

    if alerts:
        for alert in alerts:
            print(f"  [!] {alert}")
    else:
        print("  [ok] Jeu de donnees equilibre et suffisant. Lancez l entrainement.")

    print("\n  Etapes : python etl/sources/import_google_form.py <export.csv>")
    print("           PYTHONPATH=. python etl/run_etl.py")
    print("           PYTHONPATH=. python ml/train.py")


if __name__ == "__main__":
    main()
