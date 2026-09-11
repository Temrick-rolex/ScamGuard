import hashlib

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.reputation import PhoneReputation, UrlReputation
from app.services.risk_engine.engine import ReputationVerdict

DANGEROUS_VERDICTS = {"MALWARE", "PHISHING", "UNWANTED"}


def url_fingerprint(url: str) -> str:
    return hashlib.sha256(url.strip().lower().encode()).hexdigest()


def lookup_urls(db: Session, urls: list[str]) -> ReputationVerdict:
    if not urls:
        return ReputationVerdict(score=0, available=False)

    worst = 0
    explanations: list[dict[str, str]] = []
    found_any = False

    for url in urls:
        cached = db.get(UrlReputation, url_fingerprint(url))
        if cached is None:
            continue
        found_any = True
        worst = max(worst, cached.score)
        if cached.verdict in DANGEROUS_VERDICTS:
            explanations.append(
                {
                    "code": "REPUT",
                    "message": f"Lien signale comme dangereux par {cached.source}",
                }
            )

    return ReputationVerdict(score=worst, explanations=explanations, available=found_any)


def lookup_phone(db: Session, phone: str) -> ReputationVerdict:
    record = db.get(PhoneReputation, phone)
    if record is None:
        return ReputationVerdict(score=0, available=False)

    explanations = [
        {
            "code": "COMMU",
            "message": f"Numero signale {record.report_count} fois par la communaute"
            + (f" ({record.main_reason})" if record.main_reason else ""),
        }
    ]
    return ReputationVerdict(score=record.score, explanations=explanations, available=True)


def remember_url(db: Session, url: str, verdict: str, score: int, source: str) -> None:
    fingerprint = url_fingerprint(url)
    cached = db.get(UrlReputation, fingerprint)
    if cached is None:
        db.add(
            UrlReputation(url_hash=fingerprint, verdict=verdict, score=score, source=source)
        )
        return
    cached.verdict = verdict
    cached.score = score
    cached.source = source
