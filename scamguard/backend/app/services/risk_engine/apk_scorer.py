import csv
import re

from etl.sources.paths import CORPUS_HASH

SHA256 = re.compile(r"^[a-f0-9]{64}$")

PERMISSIONS_CRITIQUES = {
    "android.permission.READ_SMS": ("Lecture de vos SMS", 22),
    "android.permission.RECEIVE_SMS": ("Interception des SMS recus", 22),
    "android.permission.SEND_SMS": ("Envoi de SMS payants a votre insu", 25),
    "android.permission.BIND_ACCESSIBILITY_SERVICE": ("Controle total de l ecran", 30),
    "android.permission.SYSTEM_ALERT_WINDOW": ("Affichage par dessus les autres applications", 20),
    "android.permission.REQUEST_INSTALL_PACKAGES": ("Installation d autres applications", 20),
    "android.permission.READ_CONTACTS": ("Lecture de vos contacts", 12),
    "android.permission.RECORD_AUDIO": ("Enregistrement du microphone", 15),
    "android.permission.READ_PHONE_STATE": ("Acces a l identite du telephone", 8),
    "android.permission.CALL_PHONE": ("Passage d appels", 10),
    "android.permission.PACKAGE_USAGE_STATS": ("Suivi des applications utilisees", 12),
    "android.permission.RECEIVE_BOOT_COMPLETED": ("Demarrage automatique", 6),
}

COMBINAISONS = [
    (
        {"android.permission.BIND_ACCESSIBILITY_SERVICE", "android.permission.SYSTEM_ALERT_WINDOW"},
        "Cette combinaison permet de superposer un faux ecran de connexion et de voler vos identifiants",
        25,
    ),
    (
        {"android.permission.READ_SMS", "android.permission.RECEIVE_SMS"},
        "L application peut lire les codes de validation bancaires envoyes par SMS",
        20,
    ),
    (
        {"android.permission.SEND_SMS", "android.permission.READ_CONTACTS"},
        "L application peut envoyer des SMS a tous vos contacts",
        18,
    ),
]


class BaseHashes:
    def __init__(self) -> None:
        self._hashes: set[str] = set()
        self._charger()

    def _charger(self) -> None:
        if not CORPUS_HASH.exists():
            return
        with CORPUS_HASH.open(encoding="utf-8") as fichier:
            for ligne in csv.DictReader(fichier):
                valeur = (ligne.get("hash") or "").strip().lower()
                if SHA256.match(valeur):
                    self._hashes.add(valeur)

    @property
    def available(self) -> bool:
        return bool(self._hashes)

    @property
    def taille(self) -> int:
        return len(self._hashes)

    def connu(self, empreinte: str) -> bool:
        return empreinte.strip().lower() in self._hashes


base_hashes = BaseHashes()


def analyser_apk(empreinte: str | None, permissions: list[str] | None) -> tuple[int, list[dict]]:
    explications: list[dict] = []
    score = 0
    demandees = {p.strip() for p in (permissions or []) if p.strip()}

    if empreinte and SHA256.match(empreinte.strip().lower()):
        if base_hashes.connu(empreinte):
            explications.append(
                {
                    "code": "HASH",
                    "message": "Cette application est repertoriee comme un logiciel malveillant connu",
                }
            )
            return 100, explications
        explications.append(
            {
                "code": "HASHOK",
                "message": f"Empreinte absente de la base de {base_hashes.taille} logiciels malveillants connus",
            }
        )
    elif empreinte:
        explications.append(
            {"code": "HASHINV", "message": "L empreinte fournie n est pas un SHA-256 valide"}
        )

    for permission in sorted(demandees):
        detail = PERMISSIONS_CRITIQUES.get(permission)
        if detail:
            libelle, poids = detail
            score += poids
            explications.append({"code": "PERM", "message": libelle})

    for requises, message, poids in COMBINAISONS:
        if requises.issubset(demandees):
            score += poids
            explications.append({"code": "COMBI", "message": message})

    if not demandees and not empreinte:
        explications.append(
            {
                "code": "VIDE",
                "message": "Aucune empreinte ni permission fournie, analyse impossible",
            }
        )

    return min(score, 100), explications
