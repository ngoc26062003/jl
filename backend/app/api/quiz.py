from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.character import Character
from app.schemas.quiz import CheckIn, CheckOut, QuestionOut, QuizMode
from app.services import quiz as svc

router = APIRouter(tags=["quiz"])


def _to_kana(c: Character) -> svc.Kana:
    return svc.Kana(c.id, c.char, c.romaji, tuple(c.romaji_alt or ()))


@router.get("/lessons/{lesson_id}/quiz", response_model=list[QuestionOut])
def get_quiz(
    lesson_id: int,
    mode: QuizMode = "choice",
    count: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
):
    lesson_chars = db.scalars(
        select(Character).where(Character.lesson_id == lesson_id)
    ).all()
    if not lesson_chars:
        raise HTTPException(404, "Lesson not found or has no characters")

    all_chars = db.scalars(
        select(Character).where(Character.script == lesson_chars[0].script)
    ).all()

    questions = svc.build_questions(
        [_to_kana(c) for c in lesson_chars],
        [_to_kana(c) for c in all_chars],
        mode, count,
    )
    return [QuestionOut(**q.__dict__) for q in questions]


@router.post("/quiz/check", response_model=CheckOut)
def check_answer(body: CheckIn, db: Session = Depends(get_db)):
    c = db.get(Character, body.character_id)
    if c is None:
        raise HTTPException(404, "Character not found")
    kana = _to_kana(c)
    return CheckOut(correct=svc.is_correct(kana, body.answer), correct_answer=kana.romaji)