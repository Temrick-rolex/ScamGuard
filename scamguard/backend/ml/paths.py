from pathlib import Path

RACINE_BACKEND = Path(__file__).resolve().parents[1]
ARTEFACTS = RACINE_BACKEND / "ml" / "artifacts"

PIPELINE_SMS = ARTEFACTS / "pipeline_sms_v2.joblib"
PIPELINE_EMAIL = ARTEFACTS / "pipeline_email_v1.joblib"
PIPELINE_URL = ARTEFACTS / "pipeline_url_v1.joblib"

MODELE_SMS_JSON = ARTEFACTS / "model_sms_v2.json"
METRIQUES = ARTEFACTS / "metrics.json"

PIPELINE = PIPELINE_SMS
MODELE_JSON = MODELE_SMS_JSON
