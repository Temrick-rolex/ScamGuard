import pytest

from tests.conftest import auth_header

VISITOR_FORBIDDEN = [
    ("get", "/api/v1/me"),
    ("get", "/api/v1/me/device-settings"),
    ("get", "/api/v1/admin/users"),
]

CLIENT_FORBIDDEN = [
    ("get", "/api/v1/admin/users"),
    ("get", "/api/v1/admin/users/1"),
]


def login_admin(client, admin_user) -> str:
    response = client.post(
        "/api/v1/auth/login", json={"email": admin_user.email, "password": "Admin#2026"}
    )
    return response.json()["access_token"]


@pytest.mark.parametrize("method,path", VISITOR_FORBIDDEN)
def test_visitor_cannot_reach_protected_routes(client, method, path):
    response = getattr(client, method)(path)
    assert response.status_code == 401


@pytest.mark.parametrize("method,path", CLIENT_FORBIDDEN)
def test_client_cannot_reach_admin_routes(client, registered_client, method, path):
    response = getattr(client, method)(
        path, headers=auth_header(registered_client["access_token"])
    )
    assert response.status_code == 403


def test_client_reaches_own_profile(client, registered_client):
    response = client.get("/api/v1/me", headers=auth_header(registered_client["access_token"]))
    assert response.status_code == 200
    assert response.json()["email"] == "lesly@test.cm"


def test_admin_lists_users(client, admin_user, registered_client):
    token = login_admin(client, admin_user)
    response = client.get("/api/v1/admin/users", headers=auth_header(token))

    assert response.status_code == 200
    assert len(response.json()) >= 2


def test_admin_cannot_suspend_himself(client, admin_user):
    token = login_admin(client, admin_user)
    response = client.post(
        f"/api/v1/admin/users/{admin_user.id}/suspend?reason=test",
        headers=auth_header(token),
    )
    assert response.status_code == 403


def test_suspended_client_loses_access(client, admin_user, registered_client, db):
    from sqlalchemy import select

    from app.models import User

    token = login_admin(client, admin_user)
    target = db.scalar(select(User).where(User.email == "lesly@test.cm"))
    client.post(
        f"/api/v1/admin/users/{target.id}/suspend?reason=abus%20repete",
        headers=auth_header(token),
    )

    response = client.get("/api/v1/me", headers=auth_header(registered_client["access_token"]))
    assert response.status_code == 401
