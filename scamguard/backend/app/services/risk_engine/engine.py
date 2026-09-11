from dataclasses import dataclass, field

from app.services.risk_engine import extractor
from app.services.risk_engine.model_scorer import scorer, scorer_email, scorer_url
from app.services.risk_engine.rules import apply_rules

WEIGHT_RULES = 0.40
WEIGHT_MODEL = 0.40
WEIGHT_REPUTATION = 0.20

LEVEL_SUSPICIOUS = 40
REPUTATION_FLOOR = 60
LEVEL_DANGEROUS = 70


@dataclass
class ReputationVerdict:
    score: int
    explanations: list[dict[str, str]] = field(default_factory=list)
    available: bool = True


@dataclass
class RiskResult:
    score: int
    level: str
    confidence: str
    explanations: list[dict[str, str]]
    sources: dict[str, int | None]
    model_version: str
    extracted: dict[str, list[str]]
    recommendation: str


def level_of(score: int) -> str:
    if score >= LEVEL_DANGEROUS:
        return "DANGEREUX"
    if score >= LEVEL_SUSPICIOUS:
        return "SUSPECT"
    return "FAIBLE"


def recommendation_of(level: str, has_url: bool) -> str:
    if level == "DANGEREUX":
        return "N ouvrez aucun lien et ne repondez pas. Signalez ce contenu."
    if level == "SUSPECT":
        return "Verifiez par un canal officiel avant d agir." if has_url else "Restez prudent et ne communiquez aucun code."
    return "Aucun signe de fraude detecte. Restez vigilant malgre tout."


def analyse(
    text: str,
    reputation: ReputationVerdict | None = None,
    kind: str = "MESSAGE",
) -> RiskResult:
    rules_score, rules_explanations = apply_rules(text)

    moteur = scorer_email if kind == "EMAIL" else scorer
    model_score = moteur.score(text)

    urls = extractor.extract_urls(text)
    if kind in {"URL", "QR"} and not urls and text.strip():
        urls = [text.strip()]
    phones = extractor.extract_phones(text)
    amounts = extractor.extract_amounts(text)

    explanations = list(rules_explanations)
    if model_score is not None and model_score >= 50:
        explanations.append(
            {
                "code": "ML",
                "message": f"Le modele reconnait une formulation typique des arnaques ({model_score} sur 100)",
            }
        )

    score_url = scorer_url.score_maximum(urls) if urls else None
    if score_url is not None:
        if score_url >= 50:
            explanations.append(
                {
                    "code": "MLURL",
                    "message": f"L adresse du lien presente les caracteristiques d un site frauduleux ({score_url} sur 100)",
                }
            )
        model_score = score_url if model_score is None else max(model_score, score_url)

    reputation_available = reputation is not None and reputation.available
    if reputation_available:
        explanations.extend(reputation.explanations)

    score = fuse(rules_score, model_score, reputation.score if reputation_available else None)
    confidence = "COMPLETE" if reputation_available and model_score is not None else "REDUITE"

    if not reputation_available and urls:
        explanations.append(
            {
                "code": "DEGRADE",
                "message": "Verification externe indisponible, analyse basee sur les regles et le modele",
            }
        )

    level = level_of(score)
    return RiskResult(
        score=score,
        level=level,
        confidence=confidence,
        explanations=explanations or [{"code": "OK", "message": "Aucun signal suspect identifie"}],
        sources={
            "regles": rules_score,
            "modele": model_score,
            "reputation": reputation.score if reputation_available else None,
        },
        model_version=moteur.version,
        extracted={"liens": urls, "numeros": phones, "montants": amounts},
        recommendation=recommendation_of(level, bool(urls)),
    )


def fuse(rules_score: int, model_score: int | None, reputation_score: int | None) -> int:
    parts: list[tuple[float, int]] = [(WEIGHT_RULES, rules_score)]

    if model_score is not None:
        parts.append((WEIGHT_MODEL, model_score))
    if reputation_score is not None:
        parts.append((WEIGHT_REPUTATION, reputation_score))

    total_weight = sum(weight for weight, _ in parts)
    weighted = sum(weight * value for weight, value in parts)
    score = min(round(weighted / total_weight), 100)

    if reputation_score is not None and reputation_score >= REPUTATION_FLOOR:
        score = max(score, reputation_score - 10)

    return min(score, 100)
