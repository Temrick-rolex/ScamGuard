from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.core.deps import client_ip, require_admin
from app.db.session import get_db
from app.models import AccountStatus, User
from app.schemas.auth import UserPublic
from app.services import audit, tokens

router = APIRouter(prefix="/admin/users", tags=["Administration - comptes"])


@router.get("", response_model=list[UserPublic])
def list_users(
    search: str | None = Query(default=None, max_length=120),
    limit: int = Query(default=50, le=200),
    offset: int = Query(default=0, ge=0),
    _: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    statement = select(User).order_by(User.created_at.desc())
    if search:
        pattern = f"%{search.lower()}%"
        statement = statement.where(
            or_(User.email.ilike(pattern), User.full_name.ilike(pattern))
        )
    return list(db.scalars(statement.limit(limit).offset(offset)))


@router.get("/{user_id}", response_model=UserPublic)
def read_user(user_id: int, _: User = Depends(require_admin), db: Session = Depends(get_db)):
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Utilisateur introuvable")
    return user


@router.post("/{user_id}/suspend", response_model=UserPublic)
def suspend_user(
    user_id: int,
    request: Request,
    reason: str = Query(min_length=3, max_length=200),
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    user = _load_target(db, user_id, admin)
    user.status = AccountStatus.SUSPENDED
    tokens.revoke_all(db, user.id)
    audit.record(
        db,
        "user_suspended",
        actor_id=admin.id,
        target_type="user",
        target_id=user.id,
        detail=reason,
        ip=client_ip(request),
    )
    db.commit()
    db.refresh(user)
    return user


@router.post("/{user_id}/reactivate", response_model=UserPublic)
def reactivate_user(
    user_id: int,
    request: Request,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    user = _load_target(db, user_id, admin)
    user.status = AccountStatus.ACTIVE
    audit.record(
        db,
        "user_reactivated",
        actor_id=admin.id,
        target_type="user",
        target_id=user.id,
        ip=client_ip(request),
    )
    db.commit()
    db.refresh(user)
    return user


def _load_target(db: Session, user_id: int, admin: User) -> User:
    if user_id == admin.id:
        raise HTTPException(
            status.HTTP_403_FORBIDDEN, "Un administrateur ne peut pas se moderer lui-meme"
        )
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Utilisateur introuvable")
    return user
