from pathlib import Path

from sqlalchemy.dialects import postgresql
from sqlalchemy.schema import CreateIndex, CreateTable

from app.models import Base

SORTIE = Path(__file__).resolve().parents[2] / "database" / "02_schema_tables.sql"

ENTETE = [
    "-- ScamGuard - schema PostgreSQL 18 genere depuis les modeles SQLAlchemy",
    "-- Genere par : PYTHONPATH=. python scripts/export_schema.py",
    "-- Ne pas modifier a la main : modifiez app/models/ puis regenerez.",
    "",
    "\\connect scamguard",
    "",
    "CREATE SCHEMA IF NOT EXISTS dw;",
    "",
]


def main() -> None:
    dialecte = postgresql.dialect()
    lignes = list(ENTETE)

    for table in Base.metadata.sorted_tables:
        lignes.append(str(CreateTable(table).compile(dialect=dialecte)).strip() + ";")
        lignes.append("")

        for index in table.indexes:
            lignes.append(str(CreateIndex(index).compile(dialect=dialecte)).strip() + ";")
        if table.indexes:
            lignes.append("")

    SORTIE.write_text("\n".join(lignes), encoding="utf-8")
    print(f"{len(Base.metadata.sorted_tables)} tables ecrites dans {SORTIE}")


if __name__ == "__main__":
    main()
