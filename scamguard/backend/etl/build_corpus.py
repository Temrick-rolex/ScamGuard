import csv
import hashlib
import json
import re
from collections import Counter

from etl.extract.from_blocs import lire_blocs, lire_pipes
from etl.extract.from_emails import lire_emails
from etl.sources.paths import (
    COLLECTE_TERRAIN,
    CORPUS_EMAIL,
    CORPUS_HASH,
    CORPUS_SMS,
    CORPUS_URL,
    DOSSIER_EMAILS,
    DOSSIER_HASHES,
    DOSSIER_URLS,
    PROPRE,
    RAPPORT_NETTOYAGE,
    SMS_FRAUDE,
    SMS_LEGITIME,
    SOURCES,
    verifier_sources,
)
from etl.transform.anonymize import anonymize

LONGUEUR_MIN_TEXTE = 15
LONGUEUR_MAX_TEXTE = 1500
MAX_URLS_PAR_CLASSE = 80000


def empreinte(valeur: str) -> str:
    normalise = re.sub(r"\s+", " ", valeur.lower()).strip()
    return hashlib.sha256(normalise.encode()).hexdigest()


def ecrire(chemin, lignes, colonnes) -> None:
    PROPRE.mkdir(parents=True, exist_ok=True)
    with chemin.open("w", encoding="utf-8", newline="") as fichier:
        writer = csv.DictWriter(fichier, fieldnames=colonnes)
        writer.writeheader()
        writer.writerows(lignes)


def nettoyer_textes(brutes, anonymiser=True) -> tuple[list[dict], Counter]:
    rejets = Counter()
    vus = set()
    retenues = []

    for ligne in brutes:
        message = (ligne.get("message") or "").strip()
        etiquette = ligne.get("etiquette", "")

        if etiquette not in {"FRAUDE", "LEGITIME"}:
            rejets["etiquette_invalide"] += 1
            continue
        if len(message) < LONGUEUR_MIN_TEXTE:
            rejets["trop_court"] += 1
            continue
        if not re.search(r"[a-zA-Z]", message):
            rejets["sans_lettre"] += 1
            continue

        digest = empreinte(message)
        if digest in vus:
            rejets["doublon"] += 1
            continue
        vus.add(digest)

        retenues.append(
            {
                "message": anonymize(message)[:LONGUEUR_MAX_TEXTE] if anonymiser else message[:LONGUEUR_MAX_TEXTE],
                "etiquette": etiquette,
                "source": ligne.get("source", "inconnue"),
            }
        )

    return retenues, rejets


def lire_terrain() -> list[dict[str, str]]:
    if not COLLECTE_TERRAIN.exists():
        return []

    with COLLECTE_TERRAIN.open(encoding="utf-8-sig", newline="") as fichier:
        return [
            {
                "message": ligne["message"].strip(),
                "etiquette": ligne["etiquette"].strip().upper(),
                "source": "formulaire_collecte",
            }
            for ligne in csv.DictReader(fichier)
            if ligne.get("message") and ligne.get("etiquette")
        ]


def construire_sms() -> dict:
    brutes = (
        lire_blocs(SMS_FRAUDE, "FRAUDE")
        + lire_blocs(SMS_LEGITIME, "LEGITIME")
        + lire_terrain()
    )
    retenues, rejets = nettoyer_textes(brutes)
    ecrire(CORPUS_SMS, retenues, ["message", "etiquette", "source"])

    return {
        "brutes": len(brutes),
        "retenues": len(retenues),
        "rejets": dict(rejets),
        "par_etiquette": dict(Counter(l["etiquette"] for l in retenues)),
        "par_source": dict(Counter(l["source"] for l in retenues)),
        "fichier": str(CORPUS_SMS),
    }


def construire_emails() -> dict:
    brutes = lire_emails(sorted(DOSSIER_EMAILS.glob("emails_*.txt")))
    retenues, rejets = nettoyer_textes(brutes)
    ecrire(CORPUS_EMAIL, retenues, ["message", "etiquette", "source"])

    return {
        "brutes": len(brutes),
        "retenues": len(retenues),
        "rejets": dict(rejets),
        "par_etiquette": dict(Counter(l["etiquette"] for l in retenues)),
        "fichier": str(CORPUS_EMAIL),
    }


def construire_urls() -> dict:
    par_classe = {"FRAUDE": [], "LEGITIME": []}
    vus = set()
    rejets = Counter()

    for chemin in sorted(DOSSIER_URLS.glob("urls_*.txt")):
        for entree in lire_pipes(chemin):
            etiquette = entree["etiquette"]
            if len(par_classe[etiquette]) >= MAX_URLS_PAR_CLASSE:
                continue

            url = entree["valeur"]
            if len(url) < 8 or " " in url:
                rejets["url_invalide"] += 1
                continue

            digest = empreinte(url)
            if digest in vus:
                rejets["doublon"] += 1
                continue
            vus.add(digest)

            par_classe[etiquette].append(
                {"url": url, "etiquette": etiquette, "source": entree["source"]}
            )

    equilibre = min(len(par_classe["FRAUDE"]), len(par_classe["LEGITIME"]))
    retenues = par_classe["FRAUDE"][:equilibre] + par_classe["LEGITIME"][:equilibre]
    ecrire(CORPUS_URL, retenues, ["url", "etiquette", "source"])

    return {
        "retenues": len(retenues),
        "rejets": dict(rejets),
        "par_etiquette": {"FRAUDE": equilibre, "LEGITIME": equilibre},
        "plafond_par_classe": MAX_URLS_PAR_CLASSE,
        "fichier": str(CORPUS_URL),
    }


def construire_hashes() -> dict:
    vus = set()
    retenues = []
    rejets = Counter()

    for chemin in sorted(DOSSIER_HASHES.glob("hashes_*.txt")):
        for entree in lire_pipes(chemin):
            valeur = entree["valeur"].lower().strip()

            if not re.fullmatch(r"[0-9a-f]{32,64}", valeur):
                rejets["format_invalide"] += 1
                continue
            if valeur in vus:
                rejets["doublon"] += 1
                continue
            vus.add(valeur)

            retenues.append({"hash": valeur, "source": entree["source"]})

    ecrire(CORPUS_HASH, retenues, ["hash", "source"])
    return {"retenues": len(retenues), "rejets": dict(rejets), "fichier": str(CORPUS_HASH)}


def main() -> None:
    print("Sources declarees :")
    for nom, (presents, total) in verifier_sources().items():
        marque = "ok" if presents == total and total else "--"
        print(f"  [{marque}] {nom:22} {presents}/{total} fichiers")

    print("\nConstruction des corpus...")
    sms = construire_sms()
    print(f"  SMS     : {sms['retenues']:>7} retenus sur {sms['brutes']}")
    emails = construire_emails()
    print(f"  Emails  : {emails['retenues']:>7} retenus sur {emails['brutes']}")
    urls = construire_urls()
    print(f"  URLs    : {urls['retenues']:>7} retenues (equilibrees)")
    hashes = construire_hashes()
    print(f"  Hashes  : {hashes['retenues']:>7} retenus")

    rapport = {
        "sms": sms,
        "emails": emails,
        "urls": urls,
        "hashes": hashes,
        "sources": {
            nom: {
                "origine": info["origine"],
                "url": info["url"],
                "licence": info["licence"],
                "fichiers": [str(c) for c in info["chemins"]],
            }
            for nom, info in SOURCES.items()
        },
    }
    RAPPORT_NETTOYAGE.write_text(
        json.dumps(rapport, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    print("\nRepartition SMS    :", sms["par_etiquette"])
    print("Repartition emails :", emails["par_etiquette"])
    print("Repartition URLs   :", urls["par_etiquette"])
    print(f"\nRapport : {RAPPORT_NETTOYAGE}")


if __name__ == "__main__":
    main()
