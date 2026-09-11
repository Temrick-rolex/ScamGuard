from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.deps import require_client
from app.db.session import get_db
from app.models import User
from app.models.analysis import AnalysisType
from app.schemas.analysis import (
    AnalysisResponse,
    ApkRequest,
    EmailRequest,
    HistoryItem,
    MessageRequest,
    PhoneRequest,
    UrlRequest,
)
from app.services import analyses
from app.services.risk_engine import reputation
from app.services.risk_engine.apk_scorer import analyser_apk, base_hashes
from app.services.risk_engine.engine import analyse
from app.services.risk_engine.extractor import normalize_phone

router = APIRouter(prefix="/analyses", tags=["Analyses"])


@router.post("/message", response_model=AnalysisResponse)
def analyse_message(
    payload: MessageRequest,
    user: User = Depends(require_client),
    db: Session = Depends(get_db),
) -> AnalysisResponse:
    return _run(db, user, payload.text, AnalysisType.MESSAGE)


@router.post("/url", response_model=AnalysisResponse)
def analyse_url(
    payload: UrlRequest,
    user: User = Depends(require_client),
    db: Session = Depends(get_db),
) -> AnalysisResponse:
    return _run(db, user, payload.url, AnalysisType.URL)


@router.post("/qr", response_model=AnalysisResponse)
def analyse_qr(
    payload: UrlRequest,
    user: User = Depends(require_client),
    db: Session = Depends(get_db),
) -> AnalysisResponse:
    return _run(db, user, payload.url, AnalysisType.QR)


@router.post("/email", response_model=AnalysisResponse)
def analyse_email(
    payload: EmailRequest,
    user: User = Depends(require_client),
    db: Session = Depends(get_db),
) -> AnalysisResponse:
    return _run(db, user, payload.content, AnalysisType.EMAIL)


@router.post("/apk", response_model=AnalysisResponse)
def analyse_apk(
    payload: ApkRequest,
    user: User = Depends(require_client),
    db: Session = Depends(get_db),
) -> AnalysisResponse:
    score, explications = analyser_apk(payload.sha256, payload.permissions)
    niveau = "DANGEREUX" if score >= 70 else "SUSPECT" if score >= 40 else "FAIBLE"
    conseil = {
        "DANGEREUX": "N installez pas cette application et supprimez le fichier.",
        "SUSPECT": "Cette application demande des acces inhabituels. Installez la seulement si vous connaissez l editeur.",
        "FAIBLE": "Aucun signe alarmant. Installez uniquement depuis une source de confiance.",
    }[niveau]

    return AnalysisResponse(
        id=None,
        score=score,
        level=niveau,
        confidence="COMPLETE" if base_hashes.available and payload.sha256 else "REDUITE",
        recommendation=conseil,
        explanations=explications,
        sources={"hashes": base_hashes.taille if base_hashes.available else None, "permissions": score},
        extracted={
            "application": [payload.app_name] if payload.app_name else [],
            "permissions": list(payload.permissions),
        },
        model_version=f"apk_regles_{base_hashes.taille}",
    )


@router.post("/phone", response_model=AnalysisResponse)
def analyse_phone(
    payload: PhoneRequest,
    user: User = Depends(require_client),
    db: Session = Depends(get_db),
) -> AnalysisResponse:
    number = normalize_phone(payload.phone)
    verdict = reputation.lookup_phone(db, number)
    result = analyse(number, verdict)

    if not verdict.available:
        result.explanations = [
            {
                "code": "INCONNU",
                "message": "Ce numero n a jamais ete signale. Absence de signalement ne garantit pas la securite",
            }
        ]
    db.commit()
    return _to_response(result, None)


@router.get("/history", response_model=list[HistoryItem])
def read_history(
    limit: int = Query(default=30, le=100),
    offset: int = Query(default=0, ge=0),
    user: User = Depends(require_client),
    db: Session = Depends(get_db),
):
    return analyses.history(db, user.id, limit, offset)


def _run(db: Session, user: User, text: str, kind: AnalysisType) -> AnalysisResponse:
    try:
        result, record = analyses.run_analysis(db, user, text, kind)
    except analyses.QuotaExceeded as error:
        raise HTTPException(status.HTTP_429_TOO_MANY_REQUESTS, str(error)) from error

    db.commit()
    return _to_response(result, record.id)


def _to_response(result, analysis_id: int | None) -> AnalysisResponse:
    return AnalysisResponse(
        id=analysis_id,
        score=result.score,
        level=result.level,
        confidence=result.confidence,
        recommendation=result.recommendation,
        explanations=result.explanations,
        sources=result.sources,
        extracted=result.extracted,
        model_version=result.model_version,
    )
