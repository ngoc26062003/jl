from alembic import command
from alembic.config import Config
from sqlalchemy import select

from app.core.config import get_settings
from app.core.security import hash_password
from app.db.session import SessionLocal
from app.models import User
from app.seed_grammar_n5 import seed_grammar_n5
from app.seed_practice import seed_kana
from app.seed_n5 import seed_n5


def main() -> None:
    settings = get_settings()
    if not settings.auth_secret_key or len(settings.auth_secret_key) < 32:
        raise ValueError("AUTH_SECRET_KEY must be configured and at least 32 characters.")
    bootstrap_password = settings.bootstrap_admin_password
    if bootstrap_password and len(bootstrap_password) < 12:
        raise ValueError("BOOTSTRAP_ADMIN_PASSWORD must be at least 12 characters.")
    command.upgrade(Config("alembic.ini"), "head")
    with SessionLocal() as db:
        seed_kana(db)
        added = seed_n5(db)
        grammar_count = seed_grammar_n5(db)
        if bootstrap_password:
            bootstrap_admin = db.scalar(select(User).where(User.username == "admin"))
            if bootstrap_admin is None:
                db.add(
                    User(
                        username="admin",
                        email="admin@nagoyaka.local.invalid",
                        password_hash=hash_password(bootstrap_password),
                        role="admin",
                    )
                )
            elif bootstrap_admin.role != "admin":
                raise ValueError("The reserved bootstrap admin username is already in use.")
        db.commit()
    admin_status = (
        "admin bootstrap configured"
        if bootstrap_password
        else "no admin created (BOOTSTRAP_ADMIN_PASSWORD is unset)"
    )
    print(
        f"Database migration complete; kana decks ready; N5 vocabulary ready "
        f"({added} newly added); {grammar_count} N5 grammar lessons published; {admin_status}"
    )


if __name__ == "__main__":
    main()
