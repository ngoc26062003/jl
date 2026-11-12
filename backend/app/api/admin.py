from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import case, func, select
from sqlalchemy.orm import Session
from uuid import UUID

from app.core.security import require_admin
from app.db.session import get_db
from app.models import User
from app.models.activity import PracticeAnswer, PracticeRun
from app.models.practice import StudyItem
from app.schemas.auth import RoleUpdateIn
from app.services.streaks import PRACTICE_TIMEZONE, active_streak

router = APIRouter(prefix="/admin", tags=["administration"])


@router.get("/dashboard")
def dashboard(_: User = Depends(require_admin), db: Session = Depends(get_db)):
    total_users = db.scalar(select(func.count(User.id))) or 0
    active_learners = db.scalar(
        select(func.count(func.distinct(PracticeRun.user_id)))
        .join(User, User.id == PracticeRun.user_id)
        .where(User.role == "learner", User.is_active.is_(True))
    ) or 0
    total_runs = db.scalar(select(func.count(PracticeRun.id))) or 0

    item_stats = (
        select(
            StudyItem.id.label("id"),
            StudyItem.term.label("term"),
            StudyItem.reading.label("reading"),
            StudyItem.meaning_vi.label("meaning_vi"),
            func.count(PracticeAnswer.id).label("attempts"),
            func.sum(case((PracticeAnswer.is_correct.is_(True), 1), else_=0)).label("correct"),
            func.sum(case((PracticeAnswer.is_correct.is_(False), 1), else_=0)).label("incorrect"),
        )
        .join(PracticeAnswer, PracticeAnswer.study_item_id == StudyItem.id)
        .join(PracticeRun, PracticeRun.id == PracticeAnswer.run_id)
        .where(PracticeRun.mode != "flashcard")
        .group_by(StudyItem.id)
        .subquery()
    )
    most_correct = db.execute(
        select(item_stats).where(item_stats.c.correct > 0)
        .order_by(item_stats.c.correct.desc(), item_stats.c.attempts.desc())
        .limit(10)
    ).mappings().all()
    most_incorrect = db.execute(
        select(item_stats).where(item_stats.c.incorrect > 0)
        .order_by(item_stats.c.incorrect.desc(), item_stats.c.attempts.desc())
        .limit(10)
    ).mappings().all()

    leaderboard = db.execute(
        select(
            User.id,
            User.username,
            User.email,
            User.total_stars,
            User.current_streak,
            User.last_practiced_on,
            func.coalesce(
                func.sum(
                    case(
                        (PracticeRun.mode != "flashcard", PracticeRun.correct_count),
                        else_=0,
                    )
                ),
                0,
            ).label("correct_answers"),
        )
        .outerjoin(PracticeRun, PracticeRun.user_id == User.id)
        .where(User.role == "learner")
        .group_by(User.id)
        .order_by(
            func.coalesce(
                func.sum(
                    case(
                        (PracticeRun.mode != "flashcard", PracticeRun.correct_count),
                        else_=0,
                    )
                ),
                0,
            ).desc(),
            User.total_stars.desc(),
        )
        .limit(10)
    ).mappings().all()
    today = datetime.now(PRACTICE_TIMEZONE).date()
    leaderboard_data = []
    for row in leaderboard:
        person = dict(row)
        person["current_streak"] = active_streak(
            person["last_practiced_on"],
            person["current_streak"],
            today,
        )
        leaderboard_data.append(person)

    users = db.scalars(select(User).order_by(User.created_at.desc())).all()
    return {
        "total_users": total_users,
        "active_learners": active_learners,
        "total_runs": total_runs,
        "most_correct": [dict(row) for row in most_correct],
        "most_incorrect": [dict(row) for row in most_incorrect],
        "leaderboard": leaderboard_data,
        "users": [
            {
                "id": str(user.id),
                "username": user.username,
                "email": user.email,
                "role": user.role,
                "is_active": user.is_active,
                "total_stars": user.total_stars,
                "current_streak": active_streak(
                    user.last_practiced_on,
                    user.current_streak,
                    today,
                ),
                "last_practiced_on": user.last_practiced_on.isoformat() if user.last_practiced_on else None,
            }
            for user in users
        ],
    }


@router.patch("/users/{user_id}/role")
def update_user_role(
    user_id: UUID,
    body: RoleUpdateIn,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="Không tìm thấy người dùng.")
    if user.id == admin.id and body.role != "admin":
        raise HTTPException(status_code=409, detail="Không thể tự hạ quyền admin đang đăng nhập.")
    if user.role == "admin" and body.role != "admin":
        admin_count = db.scalar(
            select(func.count(User.id)).where(User.role == "admin", User.is_active.is_(True))
        ) or 0
        if admin_count <= 1:
            raise HTTPException(status_code=409, detail="Phải duy trì ít nhất một admin.")
    user.role = body.role
    db.commit()
    return {"id": str(user.id), "role": user.role}
