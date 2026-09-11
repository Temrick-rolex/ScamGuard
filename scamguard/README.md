# ScamGuard

Détection des fraudes numériques au Cameroun : SMS, liens, QR codes, numéros.

Projet de fin d'études — ONGBAKIAK KENDI Lesly Panelle
Institut Africain d'Informatique (IAI-Cameroun) · Stage SHADERL

## Contenu du dépôt

```
scamguard/
├── backend/     API FastAPI + moteur de risque + ETL + modèle
├── frontend/    Application Flutter (Android, web client, web admin)
├── database/    Scripts SQL PostgreSQL 18
├── datasets/    Données brutes et corpus nettoyés
└── docs/        Aperçu des écrans + fonctionnement de la sentinelle
```

## Démarrage rapide

### 1. Base de données PostgreSQL 18

```
psql -U postgres -f database/01_creation_base.sql
psql -U postgres -f database/02_schema_tables.sql
```

Changez le mot de passe dans `01_creation_base.sql` avant de l'exécuter.

### 2. Backend

```
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Dans `.env`, renseignez :

```
DATABASE_URL=postgresql+psycopg://scamguard_app:VOTRE_MDP@localhost:5432/scamguard
JWT_SECRET=<résultat de python -c "import secrets;print(secrets.token_urlsafe(64))">
```

Puis :

```
PYTHONPATH=. python scripts/seed_admin.py
PYTHONPATH=. python etl/build_corpus.py
PYTHONPATH=. python etl/load_reputation.py
PYTHONPATH=. python ml/train.py
PYTHONPATH=. uvicorn app.main:app --reload
```

Documentation interactive : http://localhost:8000/docs

### 3. Frontend

```
cd frontend
flutter create --org cm.scamguard --project-name scamguard_app .
flutter pub get
flutter run -d chrome --dart-define=API_BASE_URL=http://localhost:8000/api/v1
```

`flutter create` génère les dossiers Gradle et desktop sans écraser le code existant.

## Personnaliser l'apparence

Un seul fichier : **`frontend/lib/core/branding.dart`**

| Ce que vous voulez changer | Où |
|---|---|
| Couleur principale | `Branding.couleurPrincipale` |
| Couleurs des niveaux de risque | `couleurRisqueFaible`, `couleurRisqueSuspect`, `couleurRisqueDangereux` |
| Nom de l'application | `Branding.nomApplication` |
| Arrondi des cartes et boutons | `Branding.rayonCoins`, `Branding.rayonBoutons` |
| Police | `Branding.police` |
| N'importe quel texte affiché | classe `Textes` |

Aucune couleur n'est écrite en dur dans les écrans.

## Jeux de données

| Source | Chemin | Volume brut | Licence |
|---|---|---|---|
| UCI SMS Spam Collection | `datasets/raw/uci_sms_blocs/` | 5 548 SMS | Recherche, citation requise |
| SpamAssassin | `datasets/raw/spamassassin/` | 1 000 emails | Domaine public Apache |
| OpenPhish / URLhaus / Phishing Database | `datasets/raw/urls/` | 407 080 URLs fraude | Flux publics gratuits |
| Cisco Umbrella top 1M | `datasets/raw/urls/` | 80 000 URLs légitimes | Domaines les plus visités |
| MalwareBazaar | `datasets/raw/malwarebazaar/` | 900 empreintes SHA-256 | CC0 |

Les chemins sont déclarés dans `backend/etl/sources/paths.py`.

Corpus nettoyés produits dans `datasets/clean/` :

| Fichier | Lignes | Répartition |
|---|---|---|
| `corpus_sms.csv` | 5 121 | 657 fraude / 4 464 légitime |
| `corpus_email.csv` | 996 | 496 / 500 |
| `corpus_url.csv` | 159 976 | 79 988 / 79 988 |
| `corpus_hash.csv` | 900 | empreintes de logiciels malveillants |

Rapport de nettoyage : `datasets/clean/rapport_nettoyage.json`

## Modèle

Trois modèles entraînés de zéro. **Aucun modèle pré-entraîné n'est utilisé.**

| Modèle | Algorithme | Corpus | Rappel fraude | Précision fraude | Justesse |
|---|---|---|---|---|---|
| SMS | TF-IDF 1-2 grammes + régression logistique | 5 121 | 0,90 | 0,99 | 0,986 |
| Email | TF-IDF 1-2 grammes + régression logistique | 996 | 1,00 | 0,99 | 0,995 |
| URL | 20 caractéristiques + forêt aléatoire | 141 926 domaines | 0,87 | 0,93 | 0,900 |

Artefacts : `backend/ml/artifacts/` — `pipeline_sms_v2.joblib`, `pipeline_email_v1.joblib`,
`pipeline_url_v1.joblib`, `model_sms_v2.json` (version embarquée dans le téléphone),
`metrics.json`.

### Deux biais détectés et corrigés sur le modèle URL

Le premier entraînement donnait 99,8 % de justesse. C'était faux :

1. **Le préfixe `https`** : 100 % des URLs légitimes du corpus étaient en `https`,
   96,5 % des frauduleuses en `http`. Le modèle lisait le préfixe, pas la fraude.
2. **La longueur du chemin** : les URLs légitimes portaient un chemin ajouté
   artificiellement, les frauduleuses étaient des domaines nus. Le modèle
   apprenait « chemin long = sûr », l'inverse de la réalité.

Les deux familles de caractéristiques ont été retirées et le modèle ne travaille
plus que sur le domaine, avec déduplication par domaine. La justesse tombe à
90 % — un chiffre honnête, défendable devant un jury.

## Tests

```
cd backend && python -m pytest tests -q     # 59 tests
cd frontend && flutter test
```

## Commandes utiles

| Action | Commande |
|---|---|
| Reconstruire le corpus | `PYTHONPATH=. python etl/build_corpus.py` |
| Réentraîner le modèle | `PYTHONPATH=. python ml/train.py` |
| Statistiques de collecte | `PYTHONPATH=. python etl/stats_collecte.py <export.csv>` |
| Importer un export Google Forms | `python etl/sources/import_google_form.py <export.csv>` |
| Régénérer le SQL | `PYTHONPATH=. python scripts/export_schema.py` |

## Comptes de développement

| Rôle | Identifiants |
|---|---|
| Administrateur | `admin@scamguard.cm` / `ChangeMe#2026` |
| Client de test | `paul@test.cm` / `Secret#2026` |

Changez-les avant toute mise en ligne.

## Surveillance en arrière plan (Android)

Les SMS sont analysés **sur le téléphone**, sans que l'application soit ouverte
et sans qu'aucun message ne parte sur le réseau. Le détail complet est dans
[`docs/sentinelle_arriere_plan.md`](docs/sentinelle_arriere_plan.md).

Code natif Kotlin dans `frontend/android/app/src/main/kotlin/cm/scamguard/scamguard_app/sentinelle/` :

| Fichier | Rôle |
|---|---|
| `ReceveurSms.kt` | réveillé par Android à chaque SMS reçu |
| `ModeleLocal.kt` | rejoue le modèle TF-IDF depuis `assets/model_sms_v2.json` |
| `ReglesLocales.kt` | neuf motifs de fraude en expressions régulières |
| `Quarantaine.kt` | stockage privé des messages bloqués |
| `Alertes.kt` | notifications, deux canaux selon la gravité |
| `ServiceAppels.kt` | filtrage des appels de numéros inconnus |
| `Reglages.kt` | interrupteurs et expéditeurs de confiance |

La quarantaine est **logique** : depuis Android 4.4, seule l'application SMS par
défaut peut supprimer un message. ScamGuard avertit, il n'efface pas.

## Limite connue

Flutter et le SDK Android ne sont pas installés dans l'environnement où ce code a
été écrit : le frontend n'a pas été compilé ni exécuté sur un appareil. Le backend,
l'ETL, les trois modèles et les 59 tests ont en revanche tous été exécutés
réellement.
