from pathlib import Path

RACINE_PROJET = Path(__file__).resolve().parents[3]
DOSSIER_DATASETS = RACINE_PROJET / "datasets"

BRUT = DOSSIER_DATASETS / "raw"
PROPRE = DOSSIER_DATASETS / "clean"

DOSSIER_SMS_BLOCS = BRUT / "uci_sms_blocs"
DOSSIER_EMAILS = BRUT / "spamassassin"
DOSSIER_URLS = BRUT / "urls"
DOSSIER_HASHES = BRUT / "malwarebazaar"

UCI_SMS_SPAM = BRUT / "uci_sms" / "SMSSpamCollection"
OPENPHISH_FEED = BRUT / "openphish" / "openphish_feed.txt"
COLLECTE_TERRAIN = BRUT / "terrain" / "collecte_terrain.csv"

SMS_FRAUDE = DOSSIER_SMS_BLOCS / "sms_fraude.txt"
SMS_LEGITIME = DOSSIER_SMS_BLOCS / "sms_legitime.txt"

CORPUS_SMS = PROPRE / "corpus_sms.csv"
CORPUS_EMAIL = PROPRE / "corpus_email.csv"
CORPUS_URL = PROPRE / "corpus_url.csv"
CORPUS_HASH = PROPRE / "corpus_hash.csv"
CORPUS_NETTOYE = CORPUS_SMS

RAPPORT_NETTOYAGE = PROPRE / "rapport_nettoyage.json"

SOURCES = {
    "uci_sms": {
        "chemins": [SMS_FRAUDE, SMS_LEGITIME],
        "origine": "UCI SMS Spam Collection via export blocs",
        "url": "https://archive.ics.uci.edu/dataset/228/sms+spam+collection",
        "licence": "Recherche, citation Almeida et Gomez Hidalgo 2011",
        "fiabilite": 4,
    },
    "spamassassin": {
        "chemins": sorted(DOSSIER_EMAILS.glob("emails_*.txt")),
        "origine": "Apache SpamAssassin public corpus",
        "url": "https://spamassassin.apache.org/old/publiccorpus/",
        "licence": "Apache, usage libre",
        "fiabilite": 4,
    },
    "urls_phishing": {
        "chemins": sorted(DOSSIER_URLS.glob("urls_*.txt")),
        "origine": "OpenPhish, URLhaus, Phishing.Database, Cisco Umbrella top-1M",
        "url": "https://openphish.com/feed.txt",
        "licence": "Flux publics gratuits",
        "fiabilite": 4,
    },
    "malwarebazaar": {
        "chemins": sorted(DOSSIER_HASHES.glob("hashes_*.txt")),
        "origine": "MalwareBazaar abuse.ch, hashes SHA-256",
        "url": "https://bazaar.abuse.ch/",
        "licence": "CC0",
        "fiabilite": 5,
    },
    "formulaire_collecte": {
        "chemins": [COLLECTE_TERRAIN],
        "origine": "Collecte de terrain ScamGuard, formulaire Google Forms",
        "url": "interne",
        "licence": "Donnees du projet, anonymisees",
        "fiabilite": 5,
    },
}


def verifier_sources() -> dict[str, tuple[int, int]]:
    etat = {}
    for nom, info in SOURCES.items():
        chemins = info["chemins"]
        etat[nom] = (sum(1 for c in chemins if c.exists()), len(chemins))
    return etat
