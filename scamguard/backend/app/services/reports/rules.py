from app.models.report import ReportGroup

MIN_DISTINCT_REPORTERS = 3
MIN_VALIDATED = 1
MIN_RISK_SCORE = 40

VALID_EVIDENCE = {"TEXTE", "CAPTURE", "APPEL"}


def evidence_is_acceptable(kind: str, content: str) -> bool:
    return kind in VALID_EVIDENCE and len(content.strip()) >= 15


def meets_publication_criteria(group: ReportGroup) -> bool:
    return (
        group.report_count >= MIN_DISTINCT_REPORTERS
        and group.validated_count >= MIN_VALIDATED
    )


def missing_for_publication(group: ReportGroup) -> list[str]:
    gaps = []
    if group.report_count < MIN_DISTINCT_REPORTERS:
        manquants = MIN_DISTINCT_REPORTERS - group.report_count
        gaps.append(f"{manquants} signalement(s) supplementaire(s) requis")
    if group.validated_count < MIN_VALIDATED:
        gaps.append("validation d un moderateur requise")
    return gaps


def phone_score(report_count: int, validated_count: int) -> int:
    base = min(60, report_count * 15)
    bonus = min(40, validated_count * 20)
    return min(100, base + bonus)
