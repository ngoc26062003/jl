from uuid import UUID

from pydantic import BaseModel


class LessonAnswerIn(BaseModel):
    option_id: UUID


class LessonAnswerOut(BaseModel):
    correct: bool
    correct_answer: str
    explanation: str | None
