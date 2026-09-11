from app.services.risk_engine.engine import ReputationVerdict, analyse, fuse, level_of
from app.services.risk_engine.extractor import extract_urls, normalize_phone
from app.services.risk_engine.rules import apply_rules

FRAUD_SMS = (
    "URGENT cher client MTN votre compte MoMo sera suspendu. "
    "Confirmez votre code secret 4589 avant 24h sinon suppression"
)
LEGIT_SMS = "Bonjour, votre colis est arrive au bureau de poste. Presentez votre piece d identite"


def test_rules_detect_fraud_markers():
    score, explanations = apply_rules(FRAUD_SMS)
    codes = {item["code"] for item in explanations}

    assert score > 40
    assert "R1" in codes
    assert "R3" in codes


def test_rules_stay_quiet_on_legitimate_message():
    score, explanations = apply_rules(LEGIT_SMS)
    assert score == 0
    assert explanations == []


def test_fraud_message_is_flagged():
    result = analyse(FRAUD_SMS)
    assert result.level in {"SUSPECT", "DANGEREUX"}
    assert result.explanations


def test_legitimate_message_stays_low():
    result = analyse(LEGIT_SMS)
    assert result.level == "FAIBLE"


def test_confidence_is_reduced_without_reputation():
    result = analyse(FRAUD_SMS)
    assert result.confidence == "REDUITE"


def test_confidence_complete_with_reputation():
    verdict = ReputationVerdict(score=90, explanations=[{"code": "REPUT", "message": "test"}])
    result = analyse(FRAUD_SMS, verdict)
    assert result.confidence == "COMPLETE"


def test_fusion_redistributes_missing_sources():
    assert fuse(80, None, None) == 80
    assert fuse(80, 40, None) == 60
    assert fuse(100, 100, 100) == 100


def test_levels_follow_thresholds():
    assert level_of(10) == "FAIBLE"
    assert level_of(55) == "SUSPECT"
    assert level_of(85) == "DANGEREUX"


def test_extractor_finds_url_and_normalises_phone():
    text = "Payez sur http://mtn-momo.xyz/pay ou appelez 677 12 34 56"
    assert extract_urls(text) == ["http://mtn-momo.xyz/pay"]
    assert normalize_phone("677 12 34 56") == "+237677123456"


def test_result_always_carries_a_recommendation():
    assert analyse(FRAUD_SMS).recommendation
    assert analyse(LEGIT_SMS).recommendation


def test_strong_reputation_cannot_be_diluted():
    verdict = ReputationVerdict(score=65, explanations=[{"code": "COMMU", "message": "3 signalements"}])
    result = analyse("677889900", verdict)

    assert result.score >= 55
    assert result.level != "FAIBLE"


def test_weak_reputation_stays_a_simple_signal():
    verdict = ReputationVerdict(score=30, explanations=[])
    assert analyse("bonjour comment vas tu aujourd hui", verdict).level == "FAIBLE"
