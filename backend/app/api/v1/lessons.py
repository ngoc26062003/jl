from typing import Literal
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import and_, func, select
from sqlalchemy.orm import Session, aliased, selectinload

from app.db.session import get_db
from app.core.security import get_current_user
from app.models import Category, Lesson, Question, QuestionOption
from app.schemas import LessonDetailOut, LessonOut, LessonPage, QuestionOut
from app.schemas.lesson_answers import LessonAnswerIn, LessonAnswerOut

router = APIRouter(
    prefix="/lessons",
    tags=["lessons"],
    dependencies=[Depends(get_current_user)],
)


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


@router.get("/{lesson_id}", response_model=LessonDetailOut)
def get_lesson(lesson_id: UUID, db: Session = Depends(get_db)):
    return _get_published_lesson(db, lesson_id)


@router.get("/{lesson_id}/questions", response_model=list[QuestionOut])
def get_questions(
    lesson_id: UUID,
    mode: Literal["multiple_choice", "typing"] | None = None,
    db: Session = Depends(get_db),
):
    stmt = (
        select(Question)
        .join(Lesson, Lesson.id == Question.lesson_id)
        .where(Question.lesson_id == lesson_id, Question.is_active.is_(True))
        .where(Lesson.status == "published")
        .options(selectinload(Question.options))
        .order_by(Question.position)
    )
    if mode:
        stmt = stmt.where(Question.question_type == mode)
    return db.scalars(stmt).all()


@router.post(
    "/{lesson_id}/questions/{question_id}/answer",
    response_model=LessonAnswerOut,
)
def check_lesson_answer(
    lesson_id: UUID,
    question_id: UUID,
    body: LessonAnswerIn,
    db: Session = Depends(get_db),
):
    selected_option = aliased(QuestionOption)
    correct_option = aliased(QuestionOption)
    result = db.execute(
        select(
            selected_option.id.label("selected_id"),
            correct_option.id.label("correct_id"),
            correct_option.text.label("correct_answer"),
            Question.explanation,
        )
        .select_from(Question)
        .join(Lesson, Lesson.id == Question.lesson_id)
        .outerjoin(
            selected_option,
            and_(
                selected_option.question_id == Question.id,
                selected_option.id == body.option_id,
            ),
        )
        .outerjoin(
            correct_option,
            and_(
                correct_option.question_id == Question.id,
                correct_option.is_correct.is_(True),
            ),
        )
        .where(
            Question.id == question_id,
            Question.lesson_id == lesson_id,
            Question.is_active.is_(True),
            Lesson.status == "published",
        )
    ).one_or_none()
    if result is None:
        raise HTTPException(status_code=404, detail="Question not found")
    if result.selected_id is None or result.correct_id is None:
        raise HTTPException(status_code=422, detail="Invalid answer option")

    return LessonAnswerOut(
        correct=result.selected_id == result.correct_id,
        correct_answer=result.correct_answer,
        explanation=result.explanation,
    )