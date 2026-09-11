from datetime import timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import (
    create_access_token,
    fingerprint,
    generate_refresh_token,
)
from app.models import RefreshToken, User
from app.models.base import utc_now
from app.schemas.auth import TokenPair


class TokenReuseDetected(Exception):
    pass


def issue_pair(db: Session, user: User) -> TokenPair:
    raw_refresh = generate_refresh_token()
    db.add(
        RefreshToken(
            user_id=user.id,
            token_hash=fingerprint(raw_refresh),
            expires_at=utc_now() + timedelta(days=settings.refresh_token_days),
        )
    )
    access = create_access_token(user.id, user.role.value, user.is_premium)
    return TokenPair(
        access_token=access,
        refresh_token=raw_refresh,
        expires_in_minutes=settings.access_token_minutes,
    )


def rotate(db: Session, raw_refresh: str) -> tuple[User, TokenPair]:
    stored = db.scalar(
        select(RefreshToken).where(RefreshToken.token_hash == fingerprint(raw_refresh))
    )
    if stored is None:
        raise TokenReuseDetected("Jeton de rafraichissement inconnu")

    now = utc_now()
    if not stored.is_usable(now):
        revoke_all(db, stored.user_id)
        raise TokenReuseDetected("Jeton deja utilise ou expire, session revoquee")

    stored.revoked_at = now
    pair = issue_pair(db, stored.user)
    stored.replaced_by = fingerprint(pair.refresh_token)
    return stored.user, pair


def revoke(db: Session, raw_refresh: str) -> bool:
    stored = db.scalar(
        select(RefreshToken).where(RefreshToken.token_hash == fingerprint(raw_refresh))
    )
    if stored is None or stored.revoked_at is not None:
        return False
    stored.revoked_at = utc_now()
    return True


def revoke_all(db: Session, user_id: int) -> None:
    tokens = db.scalars(
        select(RefreshToken).where(
            RefreshToken.user_id == user_id, RefreshToken.revoked_at.is_(None)
        )
    )
    now = utc_now()
    for token in tokens:
        token.revoked_at = now
