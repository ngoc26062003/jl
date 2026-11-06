from sqlalchemy import ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Deck(Base):
    __tablename__ = "decks"

    id: Mapped[int] = mapped_column(primary_key=True)
    category: Mapped[str] = mapped_column(String(16), index=True)  # hiragana|katakana|vocab|kanji
    level: Mapped[str | None] = mapped_column(String(4), index=True)  # N5..N1, None cho kana
    slug: Mapped[str] = mapped_column(String(96), unique=True)
    title_jp: Mapped[str] = mapped_column(String(64))
    title_vi: Mapped[str] = mapped_column(String(128))
    position: Mapped[int] = mapped_column(default=0)


class StudyItem(Base):
    __tablename__ = "study_items"
    __table_args__ = (UniqueConstraint("deck_id", "term", "reading"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    deck_id: Mapped[int] = mapped_column(ForeignKey("decks.id", ondelete="CASCADE"), index=True)
    term: Mapped[str] = mapped_column(String(64))        # chữ hiển thị: あ / 学生 / 日
    reading: Mapped[str] = mapped_column(String(64))     # cách đọc bằng kana
    romaji: Mapped[str] = mapped_column(String(96))
    romaji_alt: Mapped[list[str]] = mapped_column(ARRAY(String(96)), default=list, server_default="{}")
    meaning_vi: Mapped[str | None] = mapped_column(Text)
    extra: Mapped[dict | None] = mapped_column(JSONB)    # chỗ dành cho hán tự: on/kun, ví dụ...
    position: Mapped[int] = mapped_column(default=0)