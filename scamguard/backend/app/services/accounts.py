from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.models import DeviceSettings, Role, User
from app.schemas.auth import RegisterRequest


class EmailAlreadyUsed(Exception):
    pass


class PhoneAlreadyUsed(Exception):
    pass


def find_by_email(db: Session, email: str) -> User | None:
    return db.scalar(select(User).where(User.email == email.lower()))


def create_client(db: Session, payload: RegisterRequest) -> User:
    if find_by_email(db, payload.email):
        raise EmailAlreadyUsed("Cet email est deja enregistre")

    if payload.phone and db.scalar(select(User).where(User.phone == payload.phone)):
        raise PhoneAlreadyUsed("Ce numero est deja enregistre")

    user = User(
        full_name=payload.full_name.strip(),
        email=payload.email.lower(),
        phone=payload.phone,
        password_hash=hash_password(payload.password),
        role=Role.CLIENT,
    )
    user.settings = DeviceSettings()
    db.add(user)
    db.flush()
    return user


def ensure_settings(db: Session, user: User) -> DeviceSettings:
    if user.settings is None:
        user.settings = DeviceSettings(user_id=user.id)
        db.flush()
    return user.settings
