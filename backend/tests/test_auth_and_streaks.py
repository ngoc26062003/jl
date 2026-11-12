from datetime import date

import pytest
from pydantic import ValidationError

from app.core.security import hash_password, verify_password
from app.core.security import require_admin
from app.models import User
from app.schemas.auth import LoginIn, RegisterIn
from app.services.streaks import active_streak, award_daily_streak
from fastapi import HTTPException
from uuid import uuid4


def test_login_requires_nonempty_identifier_and_password_before_endpoint_runs():
    with pytest.raises(ValidationError):
        LoginIn.model_validate({"identifier": "learner"})
    with pytest.raises(ValidationError):
        LoginIn.model_validate({"identifier": " ", "password": "secret"})
    with pytest.raises(ValidationError):
        LoginIn.model_validate({"identifier": "learner", "password": ""})


def test_registration_cannot_choose_admin_role():
    payload = RegisterIn.model_validate(
        {"username": "student_1", "email": "Student@example.com", "password": "safe-password"}
    )
    assert payload.username == "student_1"
    assert payload.email == "student@example.com"
    assert not hasattr(payload, "role")


def test_learner_cannot_pass_admin_guard():
    learner = User(
        id=uuid4(),
        username="student",
        email="student@example.com",
        role="learner",
    )
    with pytest.raises(HTTPException) as error:
        require_admin(learner)
    assert error.value.status_code == 403


def test_password_hash_is_not_reversible_and_verifies_only_matching_password():
    encoded = hash_password("a-long-password")
    assert encoded != "a-long-password"
    assert verify_password("a-long-password", encoded)
    assert not verify_password("wrong-password", encoded)
    assert not verify_password("anything", None)


def test_streak_awards_once_per_local_day_and_increments_on_consecutive_days():
    day_one = date(2026, 11, 12)
    first = award_daily_streak(None, 0, 0, day_one)
    assert first == (1, 1, day_one, False)
    same_day = award_daily_streak(first[2], first[0], first[1], day_one)
    assert same_day == (1, 1, day_one, True)
    next_day = award_daily_streak(first[2], first[0], first[1], date(2026, 11, 13))
    assert next_day == (2, 3, date(2026, 11, 13), False)


def test_streak_resets_after_a_missed_calendar_day():
    streak = award_daily_streak(
        date(2026, 11, 13), 2, 3, date(2026, 11, 15)
    )
    assert streak == (1, 4, date(2026, 11, 15), False)


def test_streak_is_not_active_after_a_missed_calendar_day():
    assert active_streak(date(2026, 11, 13), 2, date(2026, 11, 15)) == 0
    assert active_streak(date(2026, 11, 14), 2, date(2026, 11, 15)) == 2
