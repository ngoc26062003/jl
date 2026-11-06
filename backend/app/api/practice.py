from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import and_, func, or_, select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.practice import Deck, StudyItem
from app.schemas.practice import DeckOut, ItemsOut

router = APIRouter(prefix="/practice", tags=["practice"])
Category = Literal["hiragana", "katakana", "vocab", "kanji"]
MAX_DECKS = 50


@router.get("/decks", response_model=list[DeckOut])
def list_decks(
    category: list[Category] | None = Query(None),
    level: str | None = Query(None, pattern=r"^N[1-5]$"),
    db: Session = Depends(get_db),
):
    stmt = (
        select(Deck, func.count(StudyItem.id))
        .outerjoin(StudyItem, StudyItem.deck_id == Deck.id)
        .group_by(Deck.id)
        .order_by(Deck.category, Deck.position, Deck.id)
    )
    if category:
        stmt = stmt.where(Deck.category.in_(category))
    if level:
        stmt = stmt.where(Deck.level == level)
    return [
        DeckOut(id=d.id, category=d.category, level=d.level, slug=d.slug,
                title_jp=d.title_jp, title_vi=d.title_vi, item_count=n)
        for d, n in db.execute(stmt).all()
    ]


@router.get("/items", response_model=ItemsOut)
def get_items(
    deck_ids: list[int] = Query(...),
    with_distractors: bool = False,
    db: Session = Depends(get_db),
):
    if len(deck_ids) > MAX_DECKS:
        raise HTTPException(422, f"Tối đa {MAX_DECKS} bộ mỗi lần")
    decks = db.scalars(select(Deck).where(Deck.id.in_(deck_ids))).all()
    if not decks:
        raise HTTPException(404, "Không tìm thấy bộ nào")

    items = db.scalars(
        select(StudyItem)
        .where(StudyItem.deck_id.in_(deck_ids))
        .order_by(StudyItem.deck_id, StudyItem.position)
    ).all()

    distractors: list[StudyItem] = []
    if with_distractors:
        conds = [
            and_(Deck.category == c, Deck.level.is_(None) if lv is None else Deck.level == lv)
            for c, lv in {(d.category, d.level) for d in decks}
        ]
        distractors = db.scalars(
            select(StudyItem)
            .join(Deck, Deck.id == StudyItem.deck_id)
            .where(or_(*conds), StudyItem.deck_id.not_in(deck_ids))
            .order_by(func.random())
            .limit(60)
        ).all()

    return {"items": items, "distractors": distractors}