import pytest

from tests.conftest import auth_header

ARNAQUE = (
    "Cher client MTN vous avez gagne 500000 FCFA. Envoyez votre code MoMo "
    "au 677889900 pour recevoir votre gain avant ce soir"
)


def login(client, email, password="Secret#2026"):
    response = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    return response.json()["access_token"]


def admin_header(client):
    return auth_header(login(client, "admin@test.cm", "Admin#2026"))


def register(client, email):
    client.post(
        "/api/v1/auth/register",
        json={
            "full_name": "Testeur ScamGuard",
            "email": email,
            "phone": None,
            "password": "Secret#2026",
        },
    )
    response = client.post(
        "/api/v1/auth/login", json={"email": email, "password": "Secret#2026"}
    )
    return response.json()["access_token"]


def report_payload(content=ARNAQUE, **extra):
    payload = {
        "content": content,
        "reason": "FAUX_GAIN",
        "comment": "Recu ce matin par SMS",
        "evidence_kind": "TEXTE",
        "suspect_phone": "677889900",
    }
    payload.update(extra)
    return payload


def test_report_is_stored_pending(client, registered_client):
    response = client.post(
        "/api/v1/reports", json=report_payload(), headers=auth_header(registered_client["access_token"])
    )
    body = response.json()

    assert response.status_code == 201
    assert body["status"] == "EN_ATTENTE"
    assert body["published"] is False
    assert body["risk_level"] in {"SUSPECT", "DANGEREUX"}


def test_receipt_explains_what_is_missing(client, registered_client):
    response = client.post(
        "/api/v1/reports", json=report_payload(), headers=auth_header(registered_client["access_token"])
    )
    gaps = response.json()["missing_for_publication"]

    assert any("signalement" in gap for gap in gaps)
    assert any("moderateur" in gap for gap in gaps)


def test_evidence_too_short_is_refused(client, registered_client):
    response = client.post(
        "/api/v1/reports",
        json=report_payload(content="arnaque"),
        headers=auth_header(registered_client["access_token"]),
    )
    assert response.status_code == 422


def test_same_user_cannot_report_twice(client, registered_client):
    header = auth_header(registered_client["access_token"])
    client.post("/api/v1/reports", json=report_payload(), headers=header)
    second = client.post("/api/v1/reports", json=report_payload(), headers=header)

    assert second.status_code == 409


def test_reports_are_grouped_by_content(client, registered_client):
    client.post(
        "/api/v1/reports", json=report_payload(), headers=auth_header(registered_client["access_token"])
    )
    other = register(client, "temoin2@test.cm")
    response = client.post(
        "/api/v1/reports", json=report_payload(), headers=auth_header(other)
    )

    assert response.json()["report_count"] == 2


def test_stored_content_is_anonymised(client, db, registered_client):
    from app.models.report import Report

    client.post(
        "/api/v1/reports",
        json=report_payload(content=ARNAQUE + " contactez le 699112233"),
        headers=auth_header(registered_client["access_token"]),
    )
    stored = db.query(Report).first().content_redacted

    assert "699112233" not in stored
    assert "[TEL]" in stored


def test_history_is_empty_before_moderation(client, registered_client):
    client.post(
        "/api/v1/reports", json=report_payload(), headers=auth_header(registered_client["access_token"])
    )
    response = client.get("/api/v1/reports/history", headers=auth_header(registered_client["access_token"]))

    assert response.status_code == 200
    assert response.json() == []


def test_publication_requires_three_reporters_and_a_moderator(
    client, registered_client, admin_user
):
    client.post(
        "/api/v1/reports", json=report_payload(), headers=auth_header(registered_client["access_token"])
    )
    for email in ("temoin3@test.cm", "temoin4@test.cm"):
        token = register(client, email)
        client.post(
            "/api/v1/reports",
            json=report_payload(),
            headers=auth_header(token),
        )

    header = admin_header(client)
    pending = client.get("/api/v1/admin/reports/pending", headers=header).json()
    assert len(pending) == 3

    client.post(
        f"/api/v1/admin/reports/{pending[0]['id']}/approve",
        json={"note": "Arnaque confirmee"},
        headers=header,
    )

    feed = client.get("/api/v1/reports/history", headers=auth_header(registered_client["access_token"])).json()
    assert len(feed) == 1
    assert feed[0]["report_count"] == 3


def test_approval_feeds_phone_reputation(client, db, registered_client, admin_user):
    from app.models.reputation import PhoneReputation

    for email in ("temoin5@test.cm", "temoin6@test.cm"):
        token = register(client, email)
        client.post(
            "/api/v1/reports",
            json=report_payload(),
            headers=auth_header(token),
        )
    client.post(
        "/api/v1/reports", json=report_payload(), headers=auth_header(registered_client["access_token"])
    )

    header = admin_header(client)
    pending = client.get("/api/v1/admin/reports/pending", headers=header).json()
    client.post(
        f"/api/v1/admin/reports/{pending[0]['id']}/approve",
        json={"note": "Confirme"},
        headers=header,
    )

    record = db.get(PhoneReputation, "+237677889900")
    assert record is not None
    assert record.report_count == 3
    assert record.score > 0


def test_rejection_requires_a_reason(client, registered_client, admin_user):
    client.post(
        "/api/v1/reports", json=report_payload(), headers=auth_header(registered_client["access_token"])
    )
    header = admin_header(client)
    pending = client.get("/api/v1/admin/reports/pending", headers=header).json()

    response = client.post(
        f"/api/v1/admin/reports/{pending[0]['id']}/reject",
        json={"note": "   "},
        headers=header,
    )
    assert response.status_code == 422


def test_report_cannot_be_moderated_twice(client, registered_client, admin_user):
    client.post(
        "/api/v1/reports", json=report_payload(), headers=auth_header(registered_client["access_token"])
    )
    header = admin_header(client)
    report_id = client.get("/api/v1/admin/reports/pending", headers=header).json()[0]["id"]

    client.post(
        f"/api/v1/admin/reports/{report_id}/approve", json={"note": "ok"}, headers=header
    )
    again = client.post(
        f"/api/v1/admin/reports/{report_id}/reject",
        json={"note": "erreur"},
        headers=header,
    )
    assert again.status_code == 409


def test_client_cannot_reach_moderation_queue(client, registered_client):
    response = client.get(
        "/api/v1/admin/reports/pending", headers=auth_header(registered_client["access_token"])
    )
    assert response.status_code == 403


def test_visitor_cannot_read_history(client):
    assert client.get("/api/v1/reports/history").status_code == 401


def test_stats_count_reports(client, registered_client):
    client.post(
        "/api/v1/reports", json=report_payload(), headers=auth_header(registered_client["access_token"])
    )
    body = client.get("/api/v1/reports/stats", headers=auth_header(registered_client["access_token"])).json()

    assert body["signalements_recus"] == 1
    assert body["arnaques_publiees"] == 0
    assert body["numeros_suspects"] == 1
