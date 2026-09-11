import json
import math
import re
import unicodedata

import joblib
import pytest

from ml.paths import MODELE_SMS_JSON, PIPELINE_SMS

MESSAGES = [
    "URGENT MTN votre compte MoMo sera bloque confirmez votre code PIN 4589",
    "Salut on se voit a 15h au bureau comme prevu",
    "Felicitations vous avez gagne 500000 FCFA envoyez les frais de 5000",
    "Bonjour votre facture ENEO du mois de septembre est disponible",
    "Your account has been suspended click here to verify your password now",
]

TOLERANCE = 2


def sans_accent(texte: str) -> str:
    return "".join(
        c for c in unicodedata.normalize("NFD", texte) if not unicodedata.combining(c)
    )


def score_mobile(charge: dict, texte: str) -> int:
    mots = [m for m in re.split(r"[^a-z0-9]+", sans_accent(texte.lower())) if len(m) > 1]
    jetons = mots + [f"{mots[i]} {mots[i + 1]}" for i in range(len(mots) - 1)]

    comptes: dict[int, float] = {}
    for jeton in jetons:
        index = charge["vocabulaire"].get(jeton)
        if index is not None:
            comptes[index] = comptes.get(index, 0.0) + 1.0
    if not comptes:
        return 0

    pondere = {i: (1.0 + math.log(c)) * charge["idf"][i] for i, c in comptes.items()}
    norme = math.sqrt(sum(v * v for v in pondere.values()))
    if norme == 0:
        return 0

    somme = charge["biais"] + sum(
        (v / norme) * charge["poids"][i] for i, v in pondere.items()
    )
    return round(100 / (1 + math.exp(-somme)))


@pytest.fixture(scope="module")
def artefacts():
    if not PIPELINE_SMS.exists() or not MODELE_SMS_JSON.exists():
        pytest.skip("Modele SMS non entraine")
    return joblib.load(PIPELINE_SMS), json.loads(MODELE_SMS_JSON.read_text(encoding="utf-8"))


@pytest.mark.parametrize("message", MESSAGES)
def test_le_score_du_telephone_egale_celui_du_serveur(artefacts, message):
    pipeline, charge = artefacts
    index = list(pipeline.classes_).index("FRAUDE")
    attendu = round(pipeline.predict_proba([message])[0][index] * 100)
    obtenu = score_mobile(charge, message)
    assert abs(obtenu - attendu) <= TOLERANCE, f"serveur={attendu} telephone={obtenu}"


def test_un_message_frauduleux_depasse_le_seuil_dangereux(artefacts):
    _, charge = artefacts
    assert score_mobile(charge, MESSAGES[0]) >= 70


def test_un_message_normal_reste_sous_le_seuil_suspect(artefacts):
    _, charge = artefacts
    assert score_mobile(charge, MESSAGES[1]) < 40
