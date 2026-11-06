from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base  # chỉnh theo vị trí Base của bạn


class Character(Base):
    __tablename__ = "characters"

    id: Mapped[int] = mapped_column(primary_key=True)
    lesson_id: Mapped[int] = mapped_column(ForeignKey("lessons.id"), index=True)
    script: Mapped[str] = mapped_column(String(16), default="hiragana", index=True)
    char: Mapped[str] = mapped_column(String(4))
    romaji: Mapped[str] = mapped_column(String(8))
    romaji_alt: Mapped[list[str]] = mapped_column(ARRAY(String(8)), default=list)
    position: Mapped[int] = mapped_column(default=0)