from typing import Literal
from pydantic import BaseModel, Field


class QuestionOut(BaseModel):
    character_id: int
    char: str
    options: list[str] | None = None


class CheckIn(BaseModel):
    character_id: int
    answer: str = Field(max_length=16)


class CheckOut(BaseModel):
    correct: bool
    correct_answer: str


QuizMode = Literal["choice", "typing"]