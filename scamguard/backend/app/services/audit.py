from sqlalchemy.orm import Session

from app.models import AuditLog


def record(
    db: Session,
    action: str,
    actor_id: int | None = None,
    target_type: str = "",
    target_id: str = "",
    detail: str = "",
    ip: str = "unknown",
) -> None:
    db.add(
        AuditLog(
            actor_id=actor_id,
            action=action,
            target_type=target_type,
            target_id=str(target_id),
            detail=detail[:500],
            ip=ip,
        )
    )
