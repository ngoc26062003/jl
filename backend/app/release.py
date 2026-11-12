from alembic import command
from alembic.config import Config

from app.db.session import SessionLocal
from app.seed_grammar_n5 import seed_grammar_n5
from app.seed_practice import seed_kana
from app.seed_n5 import seed_n5


def main() -> None:
    command.upgrade(Config("alembic.ini"), "head")
    with SessionLocal() as db:
        seed_kana(db)
        added = seed_n5(db)
        grammar_count = seed_grammar_n5(db)
        db.commit()
    print(
        f"Database migration complete; kana decks ready; N5 vocabulary ready "
        f"({added} newly added); {grammar_count} N5 grammar lessons published"
    )


if __name__ == "__main__":
    main()
