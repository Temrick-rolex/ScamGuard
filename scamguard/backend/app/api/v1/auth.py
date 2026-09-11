from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.core.deps import client_ip, get_current_user
from app.core.security import verify_password
from app.db.session import get_db
from app.models import User
from app.schemas.auth import (
    LoginRequest,
    RefreshRequest,
    RegisterRequest,
    TokenPair,
    UserPublic,
)
from app.services import accounts, audit, login_guard, tokens

router = APIRouter(prefix="/auth", tags=["Authentification"])


@router.post("/register", response_model=UserPublic, status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest, request: Request, db: Session = Depends(get_db)) -> User:
    try:
        user = accounts.create_client(db, payload)
    except (accounts.EmailAlreadyUsed, accounts.PhoneAlreadyUsed) as error:
        raise HTTPException(status.HTTP_409_CONFLICT, str(error)) from error

    audit.record(db, "register", actor_id=user.id, target_type="user", target_id=user.id, ip=client_ip(request))
    db.commit()
    db.refresh(user)
    return user


@router.post("/login", response_model=TokenPair)
def login(payload: LoginRequest, request: Request, db: Session = Depends(get_db)) -> TokenPair:
    ip = client_ip(request)
    email = payload.email.lower()

    if login_guard.is_locked(db, email):
        db.commit()
        raise HTTPException(
            status.HTTP_429_TOO_MANY_REQUESTS,
            "Trop de tentatives echouees, reessayez dans quelques minutes",
        )

    user = accounts.find_by_email(db, email)
    valid = user is not None and verify_password(payload.password, user.password_hash)

    if not valid or user is None:
        login_guard.track(db, email, ip, successful=False)
        audit.record(db, "login_failed", target_type="email", target_id=email, ip=ip)
        db.commit()
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Identifiants incorrects")

    if not user.is_active:
        login_guard.track(db, email, ip, successful=False)
        db.commit()
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Compte suspendu ou supprime")

    login_guard.track(db, email, ip, successful=True)
    pair = tokens.issue_pair(db, user)
    audit.record(db, "login", actor_id=user.id, target_type="user", target_id=user.id, ip=ip)
    db.commit()
    return pair


@router.post("/refresh", response_model=TokenPair)
def refresh(payload: RefreshRequest, request: Request, db: Session = Depends(get_db)) -> TokenPair:
    try:
        user, pair = tokens.rotate(db, payload.refresh_token)
    except tokens.TokenReuseDetected as error:
        db.commit()
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, str(error)) from error

    audit.record(db, "token_refresh", actor_id=user.id, ip=client_ip(request))
    db.commit()
    return pair


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(
    payload: RefreshRequest,
    request: Request,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    tokens.revoke(db, payload.refresh_token)
    audit.record(db, "logout", actor_id=user.id, ip=client_ip(request))
    db.commit()
