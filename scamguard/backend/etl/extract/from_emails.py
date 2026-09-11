import re

from etl.extract.from_blocs import lire_pipes

BALISES_HTML = re.compile(r"<[^>]{1,400}>")
ENTETES = re.compile(
    r"\b(Return-Path|Delivered-To|Received|Message-I[dD]|MIME-Version|"
    r"Content-Type|Content-Transfer-Encoding|X-[\w-]+|List-[\w-]+|"
    r"Precedence|Errors-To|Sender|User-Agent|In-Reply-To|References)\s*:",
    re.I,
)
QUOTED_PRINTABLE = re.compile(r"=[0-9A-F]{2}|=\r?\n")
ESPACES = re.compile(r"\s+")

CHAMPS_UTILES = ("subject:", "from:", "to:")
LONGUEUR_MAX = 1500


def extraire_partie_lisible(brut: str) -> str:
    """Un email SpamAssassin contient des dizaines d en-tetes techniques
    qui n apportent rien au modele et ecrasent le vrai texte.
    On garde le sujet, l expediteur et le corps."""
    texte = QUOTED_PRINTABLE.sub(" ", brut)
    texte = BALISES_HTML.sub(" ", texte)

    garde = []
    for morceau in texte.split(" "):
        garde.append(morceau)

    texte = " ".join(garde)

    sujet = ""
    correspondance = re.search(r"Subject:\s*([^\n]{3,200})", brut, re.I)
    if correspondance:
        sujet = correspondance.group(1).strip()

    sans_entetes = ENTETES.sub(" ", texte)
    sans_entetes = re.sub(r"\b[\w.+-]+@[\w-]+\.[\w.]+\b", " ", sans_entetes)
    sans_entetes = re.sub(r"\b\d{1,3}(?:\.\d{1,3}){3}\b", " ", sans_entetes)
    sans_entetes = re.sub(r"\b[0-9a-f]{16,}\b", " ", sans_entetes)
    sans_entetes = ESPACES.sub(" ", sans_entetes).strip()

    complet = f"{sujet} {sans_entetes}".strip()
    return complet[:LONGUEUR_MAX]


def lire_emails(chemins) -> list[dict[str, str]]:
    lignes = []

    for chemin in chemins:
        for entree in lire_pipes(chemin):
            texte = extraire_partie_lisible(entree["valeur"])
            if len(texte) < 40:
                continue

            lignes.append(
                {
                    "message": texte,
                    "etiquette": entree["etiquette"],
                    "source": entree["source"],
                }
            )

    return lignes
