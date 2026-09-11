import json
from datetime import datetime, timezone

import joblib

from etl.sources.paths import CORPUS_EMAIL, CORPUS_SMS
from ml.paths import (
    ARTEFACTS,
    METRIQUES,
    MODELE_SMS_JSON,
    PIPELINE_EMAIL,
    PIPELINE_SMS,
)
from ml.train_texte import charger, entrainer, exporter_json_mobile
from ml.train_url import entrainer_url

RAPPEL_FRAUDE_MINIMUM = 0.85


def main() -> None:
    ARTEFACTS.mkdir(parents=True, exist_ok=True)
    resultats = {}

    corpus_sms = charger(CORPUS_SMS, minimum=100)
    resultats["sms"] = entrainer("SMS", corpus_sms, PIPELINE_SMS, min_df=2)
    exporter_json_mobile(joblib.load(PIPELINE_SMS), MODELE_SMS_JSON, "sms_v2")

    corpus_email = charger(CORPUS_EMAIL, minimum=100)
    resultats["email"] = entrainer("EMAIL", corpus_email, PIPELINE_EMAIL, min_df=1)

    resultats["url"] = entrainer_url()

    METRIQUES.write_text(
        json.dumps(
            {
                "entraine_le": datetime.now(timezone.utc).isoformat(),
                "modeles": resultats,
            },
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    print("\n=== Recapitulatif ===")
    print(f"{'Modele':8} {'Corpus':>9} {'Rappel F':>9} {'Precis F':>9} {'Exact':>8}")
    for nom, detail in resultats.items():
        print(
            f"{nom:8} {detail['corpus_total']:>9} "
            f"{detail['rappel_fraude']:>9.4f} {detail['precision_fraude']:>9.4f} "
            f"{detail['exactitude']:>8.4f}"
        )

    faibles = [
        nom
        for nom, detail in resultats.items()
        if detail["rappel_fraude"] < RAPPEL_FRAUDE_MINIMUM
    ]
    if faibles:
        print(f"\nATTENTION rappel fraude sous {RAPPEL_FRAUDE_MINIMUM} : {faibles}")

    print(f"\nMetriques : {METRIQUES}")


if __name__ == "__main__":
    main()
