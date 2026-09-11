import re
from dataclasses import dataclass

from etl.transform.normalize import clean_text


@dataclass(frozen=True)
class Rule:
    code: str
    weight: int
    explanation: str
    pattern: re.Pattern[str]


def compile_rules() -> list[Rule]:
    definitions = [
        (
            "R1",
            30,
            "Le message demande un code secret, un PIN ou un mot de passe",
            r"\b(confirm|envoy|donn|valid|saisi|communiq|transmet)\w*\b.{0,40}\b(code|pin|otp|mot de passe|password)\b"
            r"|\b(code|pin|otp|mot de passe|password)\b.{0,40}\b(confirm|envoy|donn|valid|saisi|communiq|transmet)",
        ),
        (
            "R2",
            25,
            "Le message imite un operateur ou une banque",
            r"\b(mtn|orange|momo|afriland|ecobank|uba|sgbc|camtel|eneo)\b.{0,60}\b(suspend|bloqu|desactiv|verifi|confirm|securis)",
        ),
        (
            "R3",
            20,
            "Le message cree un sentiment d urgence",
            r"\b(urgent|immediat|maintenant|avant 24h|dans 1h|derniere chance|expire|sinon)\b",
        ),
        (
            "R4",
            28,
            "Le message annonce un gain non sollicite",
            r"\b(felicitation|gagn|jackpot|tombola|selectionn|bonus|cadeau)\b.{0,60}\b(fcfa|franc|prix|lot|argent)",
        ),
        (
            "R5",
            32,
            "Le message reclame un paiement pour debloquer un gain ou un service",
            r"\b(frais|payer|paye|envoyez|deposez|versez)\b.{0,50}\b(deblo|recevoir|valid|dossier|retrait|activ)",
        ),
        (
            "R6",
            22,
            "Le message contient un lien raccourci ou un domaine douteux",
            r"(bit\.ly|tinyurl|cutt\.ly|is\.gd|t\.co/|\.xyz|\.top|\.tk|\.info)\b",
        ),
        (
            "R7",
            18,
            "Le lien imite une marque connue sans lui appartenir",
            r"\b(mtn|orange|momo|afriland|ecobank|paypal)[\w-]*\.(xyz|top|info|online|site|shop|tk)",
        ),
        (
            "R8",
            15,
            "Le message demande un transfert d argent en urgence",
            r"\b(envoi|envoy|transfer|depos)\w*\b.{0,40}\b(vite|urgent|rapidement|maintenant|bloqu)",
        ),
        (
            "R9",
            20,
            "Le message menace de sanctions ou de poursuites",
            r"\b(poursuite|judiciaire|amende|sanction|penalit|suppression|blocage definitif)\b",
        ),
        (
            "R10",
            16,
            "Le message promet un rendement financier irrealiste",
            r"\b(doubl|tripl|multipli)\w*\b.{0,40}\b(argent|investissement|capital|somme|crypto)",
        ),
    ]

    return [
        Rule(code=code, weight=weight, explanation=explanation, pattern=re.compile(pattern))
        for code, weight, explanation, pattern in definitions
    ]


RULES = compile_rules()


def apply_rules(text: str) -> tuple[int, list[dict[str, str]]]:
    normalised = clean_text(text)
    triggered: list[dict[str, str]] = []
    total = 0

    for rule in RULES:
        if rule.pattern.search(normalised):
            total += rule.weight
            triggered.append({"code": rule.code, "message": rule.explanation})

    return min(total, 100), triggered
