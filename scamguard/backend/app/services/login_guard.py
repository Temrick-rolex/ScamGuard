from datetime import timedelta

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models import LoginAttempt
from app.models.base import utc_now


def recent_failures(db: Session, email: str) -> int:
    since = utc_now() - timedelta(minutes=settings.login_window_minutes)
    statement = select(func.count()).where(
        LoginAttempt.email == email,
        LoginAttempt.successful.is_(False),
        LoginAttempt.created_at >= since,
    )
    return db.scalar(statement) or 0


def is_locked(db: Session, email: str) -> bool:
    return recent_failures(db, email) >= settings.login_max_attempts


def track(db: Session, email: str, ip: str, successful: bool) -> None:
    db.add(LoginAttempt(email=email, ip=ip, successful=successful))
