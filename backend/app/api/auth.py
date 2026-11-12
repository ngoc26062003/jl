from datetime import datetime, time, timedelta, timezone

from fastapi import APIRouter, Depends, File, HTTPException, Response, UploadFile, status
from google.auth.exceptions import GoogleAuthError
from google.auth.transport.requests import Request
from google.oauth2 import id_token
from sqlalchemy.exc import IntegrityError
from sqlalchemy import or_, select, func
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.security import (
    create_access_token,
    ensure_auth_configured,
    hash_password,
    verify_password,
    get_current_user,
)
from app.db.session import get_db
from app.models import User
from app.models.activity import MediaAsset, PracticeRun
from app.schemas.activity import PracticeHistoryOut, PracticeSummaryOut
from app.schemas.auth import AuthOut, GoogleLoginIn, LoginIn, PasswordChangeIn, RegisterIn, UserOut
from app.services.streaks import PRACTICE_TIMEZONE, active_streak
from app.services.images import MAX_UPLOAD_BYTES, normalize_uploaded_image

router = APIRouter(prefix="/auth", tags=["authentication"])
AVATAR_CONTENT_TYPE = "image/webp"


def _auth_response(user: User) -> AuthOut:
    user_data = UserOut.model_validate(user)
    user_data.current_streak = active_streak(
        user.last_practiced_on,
        user.current_streak,
        datetime.now(PRACTICE_TIMEZONE).date(),
    )
    return AuthOut(access_token=create_access_token(user), user=user_data)


@router.post("/register", response_model=AuthOut, status_code=status.HTTP_201_CREATED)
def register(body: RegisterIn, db: Session = Depends(get_db)):
    ensure_auth_configured()
    if body.username == "admin" or body.email == "admin@nagoyaka.local.invalid":
        raise HTTPException(status_code=409, detail="Tên đăng nhập hoặc email này đã được hệ thống dành riêng.")
    existing = db.scalar(
        select(User.id).where(
            or_(User.username == body.username, func.lower(User.email) == body.email)
        )
    )
    if existing is not None:
        raise HTTPException(status_code=409, detail="Tên đăng nhập hoặc email đã được sử dụng.")

    user = User(
        username=body.username,
        email=body.email,
        password_hash=hash_password(body.password),
        role="learner",
    )
    db.add(user)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Tên đăng nhập hoặc email đã được sử dụng.") from None
    db.refresh(user)
    return _auth_response(user)


@router.post("/login", response_model=AuthOut)
def login(body: LoginIn, db: Session = Depends(get_db)):
    ensure_auth_configured()
    user = db.scalar(
        select(User).where(
            or_(func.lower(User.username) == body.identifier, func.lower(User.email) == body.identifier)
        )
    )
    if user is None or not user.is_active or not verify_password(body.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Tên đăng nhập/email hoặc mật khẩu không đúng.")
    return _auth_response(user)


def _google_username(db: Session, email: str) -> str:
    base = "".join(c for c in email.partition("@")[0].lower() if c.isalnum() or c == "_")
    base = (base or "learner")[:25]
    if base == "admin":
        base = "learner"
    username = base
    suffix = 1
    while db.scalar(select(User.id).where(User.username == username)) is not None:
        username = f"{base[:25]}{suffix}"
        suffix += 1
    return username


@router.post("/google", response_model=AuthOut)
def google_login(body: GoogleLoginIn, db: Session = Depends(get_db)):
    ensure_auth_configured()
    client_id = get_settings().google_client_id
    if not client_id:
        raise HTTPException(
            status_code=503,
            detail="Đăng nhập Google chưa được cấu hình trên máy chủ.",
        )
    try:
        claims = id_token.verify_oauth2_token(body.credential, Request(), client_id)
    except (ValueError, GoogleAuthError):
        raise HTTPException(status_code=401, detail="Không xác thực được tài khoản Google.") from None

    subject = claims.get("sub")
    email = claims.get("email", "").strip().lower()
    if not subject or not email or claims.get("email_verified") is not True:
        raise HTTPException(status_code=401, detail="Google chưa xác thực địa chỉ email này.")

    user = db.scalar(select(User).where(User.google_subject == subject))
    if user is None:
        email_owner = db.scalar(select(User).where(func.lower(User.email) == email))
        if email_owner is not None:
            raise HTTPException(
                status_code=409,
                detail="Email này đã đăng ký. Hãy đăng nhập bằng phương thức đã dùng trước đó.",
            )
        user = User(
            username=_google_username(db, email),
            email=email,
            google_subject=subject,
            role="learner",
            password_hash=None,
        )
        db.add(user)
        try:
            db.commit()
        except IntegrityError:
            db.rollback()
            raise HTTPException(
                status_code=409,
                detail="Tài khoản Google hoặc email này đã được đăng ký.",
            ) from None
        db.refresh(user)
    elif not user.is_active:
        raise HTTPException(status_code=403, detail="Tài khoản không hoạt động.")

    return _auth_response(user)


@router.get("/me", response_model=UserOut)
def me(user: User = Depends(get_current_user)):
    user_data = UserOut.model_validate(user)
    user_data.current_streak = active_streak(
        user.last_practiced_on,
        user.current_streak,
        datetime.now(PRACTICE_TIMEZONE).date(),
    )
    return user_data


@router.get("/summary", response_model=PracticeSummaryOut)
def summary(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    runs = db.scalar(select(func.count(PracticeRun.id)).where(PracticeRun.user_id == user.id)) or 0
    correct = db.scalar(
        select(func.coalesce(func.sum(PracticeRun.correct_count), 0)).where(
            PracticeRun.user_id == user.id
        )
    )
    return {
        "total_runs": runs,
        "total_correct": int(correct or 0),
        "current_streak": active_streak(
            user.last_practiced_on,
            user.current_streak,
            datetime.now(PRACTICE_TIMEZONE).date(),
        ),
        "total_stars": user.total_stars,
        "last_practiced_on": user.last_practiced_on.isoformat() if user.last_practiced_on else None,
    }


@router.get("/history", response_model=PracticeHistoryOut)
def practice_history(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    today = datetime.now(PRACTICE_TIMEZONE).date()
    start_day = today - timedelta(days=34)
    start_local = datetime.combine(start_day, time.min, tzinfo=PRACTICE_TIMEZONE)
    start_utc = start_local.astimezone(timezone.utc)
    local_run_date = func.date(func.timezone(PRACTICE_TIMEZONE.key, PracticeRun.created_at))
    run_rows = db.execute(
        select(
            PracticeRun.id,
            PracticeRun.mode,
            PracticeRun.direction,
            PracticeRun.total_questions,
            PracticeRun.correct_count,
            PracticeRun.created_at,
        )
        .where(PracticeRun.user_id == user.id, PracticeRun.created_at >= start_utc)
        .order_by(PracticeRun.created_at.desc())
        .limit(30)
    ).mappings().all()
    totals = db.execute(
        select(
            func.count(PracticeRun.id).label("total_runs"),
            func.coalesce(func.sum(PracticeRun.correct_count), 0).label("total_correct"),
        ).where(PracticeRun.user_id == user.id)
    ).one()
    practice_days = db.scalars(
        select(local_run_date)
        .where(PracticeRun.user_id == user.id, PracticeRun.created_at >= start_utc)
        .group_by(local_run_date)
        .order_by(local_run_date)
    ).all()
    return {
        "runs": [dict(row) for row in run_rows],
        "practice_days": practice_days,
        "total_runs": totals.total_runs,
        "total_correct": int(totals.total_correct),
        "current_streak": active_streak(
            user.last_practiced_on,
            user.current_streak,
            today,
        ),
        "total_stars": user.total_stars,
        "last_practiced_on": user.last_practiced_on,
    }


@router.put("/password", status_code=status.HTTP_204_NO_CONTENT)
def change_password(
    body: PasswordChangeIn,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not verify_password(body.current_password, user.password_hash):
        raise HTTPException(
            status_code=400,
            detail="Mật khẩu hiện tại không đúng hoặc tài khoản này chỉ đăng nhập bằng Google.",
        )
    user.password_hash = hash_password(body.new_password)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


def _avatar_slot(user: User) -> str:
    return f"avatar:{user.id}"


@router.get("/me/avatar")
def get_avatar(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    asset = db.get(MediaAsset, _avatar_slot(user))
    if asset is None:
        raise HTTPException(status_code=404, detail="Bạn chưa tải ảnh đại diện lên.")
    return Response(
        content=asset.data,
        media_type=asset.content_type,
        headers={"Cache-Control": "private, no-cache"},
    )


@router.put("/me/avatar")
async def update_avatar(
    file: UploadFile = File(...),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    raw = await file.read(MAX_UPLOAD_BYTES + 1)
    normalized = normalize_uploaded_image(raw)
    slot = _avatar_slot(user)
    asset = db.get(MediaAsset, slot)
    if asset is None:
        asset = MediaAsset(slot=slot, content_type=AVATAR_CONTENT_TYPE, data=normalized)
        db.add(asset)
    else:
        asset.content_type = AVATAR_CONTENT_TYPE
        asset.data = normalized
    db.commit()
    return {"updated_at": asset.updated_at.isoformat() if asset.updated_at else None}
