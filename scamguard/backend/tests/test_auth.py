from tests.conftest import auth_header


def test_register_creates_client_account(client):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "full_name": "Lesly Kendi",
            "email": "Lesly@Test.CM",
            "phone": "677123456",
            "password": "Secret#2026",
        },
    )
    body = response.json()

    assert response.status_code == 201
    assert body["email"] == "lesly@test.cm"
    assert body["phone"] == "+237677123456"
    assert body["role"] == "CLIENT"


def test_register_rejects_duplicate_email(client, registered_client):
    response = client.post(
        "/api/v1/auth/register",
        json={"full_name": "Autre Personne", "email": "lesly@test.cm", "password": "Autre#2026"},
    )
    assert response.status_code == 409


def test_register_rejects_weak_password(client):
    response = client.post(
        "/api/v1/auth/register",
        json={"full_name": "Test User", "email": "faible@test.cm", "password": "motdepasse"},
    )
    assert response.status_code == 422


def test_login_returns_token_pair(client, registered_client):
    assert registered_client["access_token"]
    assert registered_client["refresh_token"]
    assert registered_client["expires_in_minutes"] == 15


def test_login_rejects_wrong_password(client, registered_client):
    response = client.post(
        "/api/v1/auth/login", json={"email": "lesly@test.cm", "password": "Mauvais#2026"}
    )
    assert response.status_code == 401


def test_login_locks_after_repeated_failures(client, registered_client):
    for _ in range(5):
        client.post("/api/v1/auth/login", json={"email": "lesly@test.cm", "password": "Faux#2026"})

    response = client.post(
        "/api/v1/auth/login", json={"email": "lesly@test.cm", "password": "Secret#2026"}
    )
    assert response.status_code == 429


def test_refresh_rotates_token(client, registered_client):
    response = client.post(
        "/api/v1/auth/refresh", json={"refresh_token": registered_client["refresh_token"]}
    )
    body = response.json()

    assert response.status_code == 200
    assert body["refresh_token"] != registered_client["refresh_token"]


def test_reusing_old_refresh_token_revokes_session(client, registered_client):
    old_token = registered_client["refresh_token"]
    client.post("/api/v1/auth/refresh", json={"refresh_token": old_token})

    response = client.post("/api/v1/auth/refresh", json={"refresh_token": old_token})
    assert response.status_code == 401


def test_logout_invalidates_refresh_token(client, registered_client):
    client.post(
        "/api/v1/auth/logout",
        json={"refresh_token": registered_client["refresh_token"]},
        headers=auth_header(registered_client["access_token"]),
    )
    response = client.post(
        "/api/v1/auth/refresh", json={"refresh_token": registered_client["refresh_token"]}
    )
    assert response.status_code == 401
