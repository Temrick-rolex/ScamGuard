import math
import re
from collections import Counter
from urllib.parse import urlparse

MARQUES = (
    "mtn", "orange", "momo", "afriland", "ecobank", "uba", "sgbc", "bicec",
    "camtel", "eneo", "paypal", "visa", "mastercard", "google", "facebook",
    "whatsapp", "apple", "microsoft", "amazon", "netflix", "instagram",
)

TLD_RISQUES = (
    "xyz", "top", "tk", "ml", "ga", "cf", "gq", "buzz", "click", "link",
    "work", "sbs", "cyou", "icu", "rest", "quest", "monster", "my", "id",
)

RACCOURCISSEURS = (
    "bit.ly", "tinyurl.com", "goo.gl", "t.co", "ow.ly", "is.gd",
    "cutt.ly", "rb.gy", "shorturl.at", "rebrand.ly",
)

MOTS_SENSIBLES = (
    "login", "signin", "verify", "verification", "secure", "account",
    "update", "confirm", "banking", "password", "wallet", "recover",
    "unlock", "suspend", "billing", "payment", "activation", "aktifasi",
)

IP_BRUTE = re.compile(r"^\d{1,3}(?:\.\d{1,3}){3}$")

# Le modele n utilise QUE le domaine. Les caracteristiques de chemin ont ete
# retirees : dans le corpus public, les URLs legitimes portent des chemins
# ajoutes artificiellement alors que les frauduleuses sont des domaines nus.
# Les garder apprenait au modele "chemin long = legitime", l inverse du reel.
NOMS = [
    "longueur_domaine", "nb_points", "nb_tirets_domaine", "nb_chiffres_domaine",
    "nb_sous_domaines", "entropie_domaine", "ratio_chiffres_domaine",
    "longueur_label_principal", "est_ip_brute", "tld_risque",
    "est_raccourcisseur", "marque_dans_domaine", "mot_sensible_domaine",
    "a_port", "domaine_tres_long", "tiret_dans_domaine", "double_tld",
    "chiffre_debut_label", "voyelles_ratio", "consonnes_consecutives",
]


def entropie(texte: str) -> float:
    if not texte:
        return 0.0
    compte = Counter(texte)
    total = len(texte)
    return -sum((n / total) * math.log2(n / total) for n in compte.values())


VOYELLES = set("aeiouy")
CONSONNES = re.compile(r"[bcdfghjklmnpqrstvwxz]{4,}")


def domaine_de(url: str) -> str:
    url = url.strip()
    if "://" not in url:
        url = "http://" + url
    return urlparse(url).netloc.lower().split(":")[0].removeprefix("www.")


def extraire(url: str) -> list[float]:
    url = url.strip()
    if "://" not in url:
        url = "http://" + url

    netloc = urlparse(url).netloc.lower()
    hote = netloc.split(":")[0].removeprefix("www.")

    parties = hote.split(".")
    tld = parties[-1] if len(parties) > 1 else ""
    label = parties[-2] if len(parties) > 1 else hote

    chiffres = sum(c.isdigit() for c in hote)
    lettres = [c for c in hote if c.isalpha()]
    voyelles = sum(c in VOYELLES for c in lettres)

    return [
        float(len(hote)),
        float(hote.count(".")),
        float(hote.count("-")),
        float(chiffres),
        float(max(0, len(parties) - 2)),
        entropie(hote),
        chiffres / len(hote) if hote else 0.0,
        float(len(label)),
        float(bool(IP_BRUTE.match(hote))),
        float(tld in TLD_RISQUES),
        float(any(r in hote for r in RACCOURCISSEURS)),
        float(any(m in hote for m in MARQUES)),
        float(any(m in hote for m in MOTS_SENSIBLES)),
        float(":" in netloc),
        float(len(hote) > 30),
        float("-" in label),
        float(len(parties) > 2 and parties[-2] in {"com", "co", "org", "net"}),
        float(label[:1].isdigit() if label else 0),
        voyelles / len(lettres) if lettres else 0.0,
        float(bool(CONSONNES.search(label))),
    ]


def extraire_lot(urls) -> list[list[float]]:
    return [extraire(u) for u in urls]
