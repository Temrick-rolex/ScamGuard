# ScamGuard API

Backend de la plateforme ScamGuard : detection et explication des fraudes numeriques mobiles.

## Installation

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Renseigner dans `.env` :
- `DATABASE_URL` : URI PostgreSQL Supabase
- `JWT_SECRET` : genere par `python -c "import secrets;print(secrets.token_urlsafe(64))"`

## Commandes

| Action | Commande |
|---|---|
| Creer l administrateur | `PYTHONPATH=. python scripts/seed_admin.py` |
| Lancer l API | `PYTHONPATH=. uvicorn app.main:app --reload` |
| Lancer les tests | `pytest tests -q` |
| Executer le pipeline ETL | `PYTHONPATH=. python etl/run_etl.py` |
| Entrainer le modele | `PYTHONPATH=. python ml/train.py` |

Documentation interactive : http://localhost:8000/docs

## Structure

```
app/       API FastAPI (core, models, schemas, services, api/v1)
etl/       Pipeline ETL : extract, transform, load, sources
ml/        Entrainement et evaluation du modele
scripts/   Utilitaires d amorcage
tests/     Tests unitaires et matrice RBAC
```

## Sources de donnees ETL

| Fichier attendu | Colonnes | Source |
|---|---|---|
| `etl/sources/public_sms.csv` | `text`, `label` | Datasets publics |
| `etl/sources/collecte_terrain.csv` | `message`, `etiquette` | Formulaire de collecte |
| Base applicative | — | Signalements valides |

Etiquettes acceptees : `FRAUDE`, `LEGITIME`, `DOUTEUX`.

## Artefacts du modele

| Fichier | Usage |
|---|---|
| `ml/artifacts/pipeline_v1.joblib` | Inference cote serveur |
| `ml/artifacts/model_v1.json` | Export embarque pour Flutter (scoring hors ligne) |
| `ml/artifacts/metrics_v1.json` | Metriques d evaluation |
