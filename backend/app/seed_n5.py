import csv
import re
from pathlib import Path

from sqlalchemy.orm import Session


DATA_FILE = Path(__file__).with_name("data") / "vocab_n5.csv"
EXPECTED_N5_COUNT = 674
KANA_ONLY = re.compile(r"^[\u3040-\u309F\u30A0-\u30FF\u30FC\s]+$")
REQUIRED_FIELDS = {
    "source_id",
    "term",
    "reading",
    "romaji",
    "meaning_en",
    "meaning_vi",
}


def load_n5_rows(path: Path = DATA_FILE) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        if not reader.fieldnames or not REQUIRED_FIELDS.issubset(reader.fieldnames):
            raise ValueError(f"N5 vocabulary CSV must contain: {', '.join(sorted(REQUIRED_FIELDS))}")
        rows = list(reader)

    if len(rows) != EXPECTED_N5_COUNT:
        raise ValueError(f"Expected {EXPECTED_N5_COUNT} N5 words, found {len(rows)}")

    seen: set[tuple[str, str]] = set()
    source_ids: set[str] = set()
    for line, row in enumerate(rows, start=2):
        if any(not (row.get(field) or "").strip() for field in REQUIRED_FIELDS):
            raise ValueError(f"N5 vocabulary CSV line {line} has an empty required field")
        key = (row["term"], row["reading"])
        if key in seen or row["source_id"] in source_ids:
            raise ValueError(f"N5 vocabulary CSV line {line} contains a duplicate word or source ID")
        if not KANA_ONLY.fullmatch(row["reading"]):
            raise ValueError(f"N5 vocabulary CSV line {line} has a non-kana reading")
        seen.add(key)
        source_ids.add(row["source_id"])

    return rows


def seed_n5(db: Session) -> int:
    from app.seed_practice import upsert_deck, upsert_items

    rows = load_n5_rows()
    deck = upsert_deck(
        db,
        slug="vocab-n5-all",
        category="vocab",
        level="N5",
        title_jp="語彙 N5",
        title_vi="Từ vựng N5 · 674 từ",
        position=0,
    )
    items = [
        {
            "term": row["term"],
            "reading": row["reading"],
            "romaji": row["romaji"],
            "romaji_alt": [],
            "meaning_vi": row["meaning_vi"],
            "extra": {
                "source": "OpenJLPT 0.3.0",
                "source_id": row["source_id"],
                "meaning_en": row["meaning_en"],
                "translation": "Machine-translated from English",
            },
        }
        for row in rows
    ]
    return upsert_items(db, deck, items)


def main() -> None:
    from app.db.session import SessionLocal

    with SessionLocal() as db:
        added = seed_n5(db)
        db.commit()
    print(f"N5 vocabulary ready: {EXPECTED_N5_COUNT} words ({added} newly added)")


if __name__ == "__main__":
    main()
