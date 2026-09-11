from sqlalchemy import select

from app.core.config import settings
from app.core.security import hash_password
from app.db.session import SessionLocal, engine
from app.models import Base, DeviceSettings, Role, User


def main() -> None:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        existing = db.scalar(select(User).where(User.email == settings.admin_email))
        if existing:
            print(f"Administrateur deja present : {existing.email}")
            return

        admin = User(
            full_name="Administrateur ScamGuard",
            email=settings.admin_email,
            password_hash=hash_password(settings.admin_password),
            role=Role.ADMIN,
        )
        admin.settings = DeviceSettings()
        db.add(admin)
        db.commit()
        print(f"Administrateur cree : {admin.email}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
