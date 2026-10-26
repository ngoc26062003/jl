from typing import Literal
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.db.session import get_db
from app.models import Category, Lesson, Question
from app.schemas import LessonOut, LessonPage, QuestionOut

router = APIRouter(prefix="/lessons", tags=["lessons"])


def _get_published_lesson(db: Session, lesson_id: UUID) -> Lesson:
    lesson = db.scalar(
        select(Lesson).where(Lesson.id == lesson_id, Lesson.status == "published")
    )
    if lesson is None:
        raise HTTPException(status_code=404, detail="Lesson not found")
    return lesson


@router.get("", response_model=LessonPage)
def list_lessons(
    category: str | None = None,
    level: str | None = None,
    lesson_type: str | None = None,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    stmt = select(Lesson).join(Category).where(Lesson.status == "published")
    if category:
        stmt = stmt.where(Category.slug == category)
    if level:
        stmt = stmt.where(Lesson.level == level)
    if lesson_type:
        stmt = stmt.where(Lesson.lesson_type == lesson_type)

    total = db.scalar(select(func.count()).select_from(stmt.subquery()))
    items = db.scalars(
        stmt.order_by(Lesson.position, Lesson.slug).limit(limit).offset(offset)
    ).all()
    return {"items": items, "total": total, "limit": limit, "offset": offset}


@router.get("/{lesson_id}", response_model=LessonOut)
def get_lesson(lesson_id: UUID, db: Session = Depends(get_db)):
    return _get_published_lesson(db, lesson_id)


@router.get("/{lesson_id}/questions", response_model=list[QuestionOut])
def get_questions(
    lesson_id: UUID,
    mode: Literal["multiple_choice", "typing"] | None = None,
    db: Session = Depends(get_db),
):
    _get_published_lesson(db, lesson_id)
    stmt = (
        select(Question)
        .where(Question.lesson_id == lesson_id, Question.is_active.is_(True))
        .options(selectinload(Question.options))
        .order_by(Question.position)
    )
    if mode:
        stmt = stmt.where(Question.question_type == mode)
    return db.scalars(stmt).all()