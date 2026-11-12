from datetime import date, datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class PracticeAnswerIn(BaseModel):
    item_id: int = Field(gt=0)
    given: str | None = Field(default=None, max_length=300)


class PracticeRunIn(BaseModel):
    mode: Literal["choice", "typing", "flashcard"]
    direction: Literal[
        "term_to_romaji", "romaji_to_term", "term_to_meaning", "typing"
    ]
    answers: list[PracticeAnswerIn] = Field(min_length=1, max_length=1000)


class PracticeRunOut(BaseModel):
    id: UUID
    total_questions: int
    correct_count: int
    current_streak: int
    total_stars: int
    practiced_today: bool


class PracticeSummaryOut(BaseModel):
    total_runs: int
    total_correct: int
    current_streak: int
    total_stars: int
    last_practiced_on: str | None


class PracticeHistoryEntryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    mode: str
    direction: str
    total_questions: int
    correct_count: int
    created_at: datetime


class PracticeHistoryOut(BaseModel):
    runs: list[PracticeHistoryEntryOut]
    practice_days: list[date]
