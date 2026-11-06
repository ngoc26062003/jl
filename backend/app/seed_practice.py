from sqlalchemy import select
from sqlalchemy.orm import Session
from app.db.session import SessionLocal        
from app.models.practice import Deck, StudyItem


KANA_ROWS = [
    ("あ", "ア", "あいうえお", "アイウエオ", ["a", "i", "u", "e", "o"]),
    ("か", "カ", "かきくけこ", "カキクケコ", ["ka", "ki", "ku", "ke", "ko"]),
    ("さ", "サ", "さしすせそ", "サシスセソ", ["sa", "shi", "su", "se", "so"]),
    ("た", "タ", "たちつてと", "タチツテト", ["ta", "chi", "tsu", "te", "to"]),
    ("な", "ナ", "なにぬねの", "ナニヌネノ", ["na", "ni", "nu", "ne", "no"]),
    ("は", "ハ", "はひふへほ", "ハヒフヘホ", ["ha", "hi", "fu", "he", "ho"]),
    ("ま", "マ", "まみむめも", "マミムメモ", ["ma", "mi", "mu", "me", "mo"]),
    ("や", "ヤ", "やゆよ", "ヤユヨ", ["ya", "yu", "yo"]),
    ("ら", "ラ", "らりるれろ", "ラリルレロ", ["ra", "ri", "ru", "re", "ro"]),
    ("わ", "ワ", "わをん", "ワヲン", ["wa", "wo", "n"]),
]
ALT = {"wo": ["o"], "n": ["nn"]}


def upsert_deck(db: Session, *, slug, category, level, title_jp, title_vi, position) -> Deck:
    deck = db.scalar(select(Deck).where(Deck.slug == slug))
    if deck is None:
        deck = Deck(slug=slug, category=category, level=level,
                    title_jp=title_jp, title_vi=title_vi, position=position)
        db.add(deck)
        db.flush()
    return deck


def upsert_items(db: Session, deck: Deck, rows: list[dict]) -> int:
    existing = {(i.term, i.reading) for i in db.scalars(select(StudyItem).where(StudyItem.deck_id == deck.id))}
    added = 0
    for pos, r in enumerate(rows):
        key = (r["term"], r["reading"])
        if key in existing:
            continue
        db.add(StudyItem(deck_id=deck.id, position=pos, **r))
        existing.add(key)
        added += 1
    return added


def seed_kana(db: Session) -> None:
    for script, head_i, chars_i in (("hiragana", 0, 2), ("katakana", 1, 3)):
        for pos, row in enumerate(KANA_ROWS):
            head, chars, romaji = row[head_i], row[chars_i], row[4]
            deck = upsert_deck(
                db, slug=f"{script}-{romaji[0]}", category=script, level=None,
                title_jp=f"{head}行", title_vi=f"Hàng {head} ({', '.join(romaji)})", position=pos,
            )
            upsert_items(db, deck, [
                dict(term=c, reading=c, romaji=r, romaji_alt=ALT.get(r, []), meaning_vi=None, extra=None)
                for c, r in zip(chars, romaji)
            ])


if __name__ == "__main__":
    with SessionLocal() as session:
        seed_kana(session)
        session.commit()
    print("Đã seed Hiragana + Katakana")