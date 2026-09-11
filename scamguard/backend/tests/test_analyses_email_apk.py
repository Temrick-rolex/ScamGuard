HASH_MALVEILLANT_ABSENT = "a" * 64

EMAIL_FRAUDULEUX = (
    "Sujet: Votre compte a ete suspendu. "
    "Cher client, nous avons detecte une activite inhabituelle. "
    "Cliquez immediatement sur ce lien pour confirmer votre mot de passe "
    "et vos informations bancaires sous 24 heures sinon votre compte sera ferme."
)

EMAIL_NORMAL = (
    "Sujet: Compte rendu de la reunion de lundi. "
    "Bonjour, voici le resume des points abordes hier avec l equipe. "
    "Le planning du trimestre est joint. Bonne journee a tous."
)


def entetes(client_enregistre):
    return {"Authorization": f"Bearer {client_enregistre['access_token']}"}


def test_email_frauduleux_est_signale(client, registered_client):
    reponse = client.post(
        "/api/v1/analyses/email",
        json={"content": EMAIL_FRAUDULEUX},
        headers=entetes(registered_client),
    )
    assert reponse.status_code == 200
    corps = reponse.json()
    assert corps["level"] in {"SUSPECT", "DANGEREUX"}
    assert corps["explanations"]


def test_email_normal_reste_faible(client, registered_client):
    reponse = client.post(
        "/api/v1/analyses/email",
        json={"content": EMAIL_NORMAL},
        headers=entetes(registered_client),
    )
    assert reponse.status_code == 200
    assert reponse.json()["level"] == "FAIBLE"


def test_email_trop_court_est_refuse(client, registered_client):
    reponse = client.post(
        "/api/v1/analyses/email",
        json={"content": "bonjour"},
        headers=entetes(registered_client),
    )
    assert reponse.status_code == 422


def test_email_exige_authentification(client):
    reponse = client.post("/api/v1/analyses/email", json={"content": EMAIL_NORMAL})
    assert reponse.status_code == 401


def test_apk_permissions_dangereuses(client, registered_client):
    reponse = client.post(
        "/api/v1/analyses/apk",
        json={
            "app_name": "Cadeau MTN",
            "permissions": [
                "android.permission.BIND_ACCESSIBILITY_SERVICE",
                "android.permission.SYSTEM_ALERT_WINDOW",
                "android.permission.READ_SMS",
                "android.permission.RECEIVE_SMS",
                "android.permission.SEND_SMS",
            ],
        },
        headers=entetes(registered_client),
    )
    assert reponse.status_code == 200
    corps = reponse.json()
    assert corps["level"] == "DANGEREUX"
    assert any(e["code"] == "COMBI" for e in corps["explanations"])


def test_apk_permissions_banales(client, registered_client):
    reponse = client.post(
        "/api/v1/analyses/apk",
        json={"app_name": "Calculatrice", "permissions": ["android.permission.INTERNET"]},
        headers=entetes(registered_client),
    )
    assert reponse.status_code == 200
    assert reponse.json()["level"] == "FAIBLE"


def test_apk_hash_inconnu_est_signale_comme_absent(client, registered_client):
    reponse = client.post(
        "/api/v1/analyses/apk",
        json={"sha256": HASH_MALVEILLANT_ABSENT, "permissions": []},
        headers=entetes(registered_client),
    )
    assert reponse.status_code == 200
    codes = [e["code"] for e in reponse.json()["explanations"]]
    assert "HASHOK" in codes or "VIDE" in codes


def test_apk_sans_donnee_reste_prudent(client, registered_client):
    reponse = client.post(
        "/api/v1/analyses/apk",
        json={"permissions": []},
        headers=entetes(registered_client),
    )
    assert reponse.status_code == 200
    corps = reponse.json()
    assert corps["score"] == 0
    assert any(e["code"] == "VIDE" for e in corps["explanations"])
