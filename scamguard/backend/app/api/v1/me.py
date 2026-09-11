from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.deps import client_ip, get_current_user
from app.core.security import hash_password, verify_password
from app.db.session import get_db
from app.models import AccountStatus, User
from app.schemas.auth import DeviceSettingsPublic, DeviceSettingsUpdate, UserPublic
from app.services import accounts, audit, tokens

router = APIRouter(prefix="/me", tags=["Mon compte"])


class ProfileUpdate(BaseModel):
    full_name: str | None = Field(default=None, min_length=3, max_length=120)
    phone: str | None = Field(default=None, max_length=20)


class PasswordChange(BaseModel):
    current_password: str
    new_password: str = Field(min_length=8, max_length=128)


@router.get("", response_model=UserPublic)
def read_profile(user: User = Depends(get_current_user)) -> User:
    return user


@router.patch("", response_model=UserPublic)
def update_profile(
    payload: ProfileUpdate,
    request: Request,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> User:
    if payload.full_name is not None:
        user.full_name = payload.full_name.strip()
    if payload.phone is not None:
        user.phone = payload.phone

    audit.record(db, "profile_update", actor_id=user.id, ip=client_ip(request))
    db.commit()
    db.refresh(user)
    return user


@router.post("/password", status_code=status.HTTP_204_NO_CONTENT)
def change_password(
    payload: PasswordChange,
    request: Request,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    if not verify_password(payload.current_password, user.password_hash):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Mot de passe actuel incorrect")

    user.password_hash = hash_password(payload.new_password)
    tokens.revoke_all(db, user.id)
    audit.record(db, "password_change", actor_id=user.id, ip=client_ip(request))
    db.commit()


@router.get("/device-settings", response_model=DeviceSettingsPublic)
def read_settings(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    settings = accounts.ensure_settings(db, user)
    db.commit()
    return settings


@router.patch("/device-settings", response_model=DeviceSettingsPublic)
def update_settings(
    payload: DeviceSettingsUpdate,
    request: Request,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    settings = accounts.ensure_settings(db, user)
    changes = payload.model_dump(exclude_none=True)
    for field, value in changes.items():
        setattr(settings, field, value)

    audit.record(db, "consent_update", actor_id=user.id, detail=str(changes), ip=client_ip(request))
    db.commit()
    db.refresh(settings)
    return settings


@router.delete("", status_code=status.HTTP_204_NO_CONTENT)
def delete_account(
    request: Request,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    user.status = AccountStatus.DELETED
    user.email = f"deleted-{user.id}@scamguard.local"
    user.phone = None
    user.full_name = "Compte supprime"
    tokens.revoke_all(db, user.id)
    audit.record(db, "account_deleted", actor_id=user.id, ip=client_ip(request))
    db.commit()
