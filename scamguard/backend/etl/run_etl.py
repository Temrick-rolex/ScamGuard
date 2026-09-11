import argparse
from pathlib import Path

from sqlalchemy.orm import Session

from app.db.session import SessionLocal, engine
from app.models import Base, EtlRun
from app.models.base import utc_now
from etl.extract.from_csv import read_labelled_csv
from etl.extract.from_reports import read_validated_reports
from etl.load.dimensions import ensure_reference_data
from etl.load.warehouse import load_facts
from etl.transform.pipeline import RawRecord, transform_batch
from etl.transform.quality import balance_report

SCRIPT_VERSION = "1.0"
SOURCES_DIR = Path(__file__).parent / "sources"


def collect(db: Session) -> list[RawRecord]:
    records: list[RawRecord] = []

    records += read_labelled_csv(
        SOURCES_DIR / "public_sms.csv",
        text_column="text",
        label_column="label",
        source="datasets_publics",
    )
    records += read_labelled_csv(
        SOURCES_DIR / "collecte_terrain.csv",
        text_column="message",
        label_column="etiquette",
        source="formulaire_collecte",
    )
    records += read_validated_reports(db)

    return records


def run() -> None:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        ensure_reference_data(db)
        run_row = EtlRun(script_version=SCRIPT_VERSION)
        db.add(run_row)
        db.flush()

        raw = collect(db)
        accepted, rejected = transform_batch(raw)
        inserted, duplicates = load_facts(db, accepted, run_row.run_id)

        run_row.rows_extracted = len(raw)
        run_row.rows_loaded = inserted
        run_row.rows_rejected = len(rejected) + duplicates
        run_row.ended_at = utc_now()
        run_row.notes = f"equilibre={balance_report([r.label for r in accepted])}"
        db.commit()

        report(run_row, rejected, duplicates)
    finally:
        db.close()


def report(run_row: EtlRun, rejected: list, duplicates: int) -> None:
    print(f"Run ETL #{run_row.run_id} (version {run_row.script_version})")
    print(f"  extraits    : {run_row.rows_extracted}")
    print(f"  charges     : {run_row.rows_loaded}")
    print(f"  rejetes     : {len(rejected)} (dont doublons deja en base : {duplicates})")
    print(f"  {run_row.notes}")

    if rejected:
        reasons: dict[str, int] = {}
        for item in rejected:
            reasons[item.reason] = reasons.get(item.reason, 0) + 1
        print(f"  motifs de rejet : {reasons}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Pipeline ETL ScamGuard")
    parser.parse_args()
    run()
