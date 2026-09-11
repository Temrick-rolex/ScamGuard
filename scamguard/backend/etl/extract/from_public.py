from urllib.parse import urlparse

from etl.sources.paths import OPENPHISH_FEED, UCI_SMS_SPAM

ETIQUETTES_UCI = {"spam": "FRAUDE", "ham": "LEGITIME"}


def lire_uci_sms() -> list[dict[str, str]]:
    """Messages SMS reels du corpus UCI. Format : etiquette TAB texte."""
    if not UCI_SMS_SPAM.exists():
        return []

    lignes = []
    with UCI_SMS_SPAM.open(encoding="utf-8", errors="ignore") as fichier:
        for ligne in fichier:
            morceaux = ligne.rstrip("\n").split("\t", 1)
            if len(morceaux) != 2:
                continue

            etiquette = ETIQUETTES_UCI.get(morceaux[0].strip().lower())
            if etiquette is None:
                continue

            lignes.append(
                {
                    "message": morceaux[1].strip(),
                    "etiquette": etiquette,
                    "source": "uci_sms_spam",
                }
            )
    return lignes


def lire_urls_phishing() -> list[dict[str, str]]:
    """URLs de phishing reelles. Elles alimentent la table de reputation,
    jamais le corpus d entrainement du modele de texte."""
    if not OPENPHISH_FEED.exists():
        return []

    urls = []
    vus = set()

    for ligne in OPENPHISH_FEED.read_text(encoding="utf-8", errors="ignore").splitlines():
        url = ligne.strip()
        if not url.startswith("http"):
            continue

        domaine = urlparse(url).netloc.lower()
        if not domaine or domaine in vus:
            continue

        vus.add(domaine)
        urls.append({"url": url, "domaine": domaine, "source": "openphish"})

    return urls
