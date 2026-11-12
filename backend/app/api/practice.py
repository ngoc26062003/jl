from datetime import datetime
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import and_, func, or_, select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.security import get_current_user
from app.models import User
from app.models.activity import PracticeAnswer, PracticeRun
from app.models.practice import Deck, StudyItem
from app.schemas.activity import PracticeRunIn, PracticeRunOut
from app.schemas.practice import DeckOut, ItemsOut
from app.services.grading import is_correct, normalize_answer
from app.services.streaks import PRACTICE_TIMEZONE, award_daily_streak

router = APIRouter(
    prefix="/practice",
    tags=["practice"],
    dependencies=[Depends(get_current_user)],
)
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


@router.post("/runs", response_model=PracticeRunOut)
def record_run(
    body: PracticeRunIn,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    item_ids = [answer.item_id for answer in body.answers]
    if len(set(item_ids)) != len(item_ids):
        raise HTTPException(status_code=422, detail="Câu trả lời bị trùng.")
    if body.mode == "typing" and body.direction != "typing":
        raise HTTPException(status_code=422, detail="Hướng luyện tập không hợp lệ.")
    if body.mode != "typing" and body.direction == "typing":
        raise HTTPException(status_code=422, detail="Hướng luyện tập không hợp lệ.")

    items = {
        item.id: item
        for item in db.scalars(select(StudyItem).where(StudyItem.id.in_(item_ids)))
    }
    if len(items) != len(item_ids):
        raise HTTPException(status_code=422, detail="Có mục luyện tập không hợp lệ.")

    graded: list[tuple[StudyItem, str | None, bool]] = []
    for submitted in body.answers:
        item = items[submitted.item_id]
        given = submitted.given or ""
        if body.mode == "flashcard":
            correct = given == "remembered"
            given = "Đã nhớ" if correct else "Chưa nhớ"
        elif body.mode == "typing":
            correct = is_correct(given, [item.romaji, *(item.romaji_alt or [])])
        elif body.direction == "term_to_romaji":
            correct = normalize_answer(given) == normalize_answer(item.romaji)
        elif body.direction == "romaji_to_term":
            correct = normalize_answer(given) == normalize_answer(item.term)
        else:
            correct = bool(item.meaning_vi) and normalize_answer(given) == normalize_answer(item.meaning_vi)
        graded.append((item, given[:300] or None, correct))

    locked_user = db.scalar(
        select(User).where(User.id == user.id).with_for_update()
    )
    if locked_user is None or not locked_user.is_active:
        raise HTTPException(status_code=401, detail="Tài khoản không hoạt động.")
    today = datetime.now(PRACTICE_TIMEZONE).date()
    (
        locked_user.current_streak,
        locked_user.total_stars,
        locked_user.last_practiced_on,
        practiced_today,
    ) = award_daily_streak(
        locked_user.last_practiced_on,
        locked_user.current_streak,
        locked_user.total_stars,
        today,
    )

    correct_count = sum(1 for _, _, correct in graded if correct)
    run = PracticeRun(
        user_id=locked_user.id,
        mode=body.mode,
        direction=body.direction,
        total_questions=len(graded),
        correct_count=correct_count,
    )
    db.add(run)
    db.flush()
    db.add_all(
        [
            PracticeAnswer(
                run_id=run.id,
                study_item_id=item.id,
                is_correct=correct,
                given=given,
                position=position,
            )
            for position, (item, given, correct) in enumerate(graded)
        ]
    )
    db.commit()
    return PracticeRunOut(
        id=run.id,
        total_questions=run.total_questions,
        correct_count=run.correct_count,
        current_streak=locked_user.current_streak,
        total_stars=locked_user.total_stars,
        practiced_today=practiced_today,
    )