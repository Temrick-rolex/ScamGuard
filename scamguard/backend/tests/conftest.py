import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.security import hash_password
from app.db.session import get_db
from app.main import app
from app.models import Base, DeviceSettings, Role, User

engine = create_engine(
    "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
)
TestingSession = sessionmaker(bind=engine, autoflush=False, autocommit=False)


@pytest.fixture(autouse=True)
def fresh_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db():
    session = TestingSession()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def client():
    def override():
        session = TestingSession()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def admin_user(db) -> User:
    admin = User(
        full_name="Admin Test",
        email="admin@test.cm",
        password_hash=hash_password("Admin#2026"),
        role=Role.ADMIN,
    )
    admin.settings = DeviceSettings()
    db.add(admin)
    db.commit()
    db.refresh(admin)
    return admin


@pytest.fixture
def registered_client(client) -> dict:
    payload = {
        "full_name": "Lesly Kendi",
        "email": "lesly@test.cm",
        "phone": "677123456",
        "password": "Secret#2026",
    }
    client.post("/api/v1/auth/register", json=payload)
    response = client.post(
        "/api/v1/auth/login", json={"email": payload["email"], "password": payload["password"]}
    )
    return response.json()


def auth_header(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}
