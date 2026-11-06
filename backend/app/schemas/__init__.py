from uuid import UUID
from pydantic import BaseModel, ConfigDict


class OptionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    text: str
    # CỐ Ý không có is_correct và explanation: tránh lộ đáp án trước khi nộp bài


class QuestionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    question_type: str
    prompt: dict
    position: int
    difficulty: int
    options: list[OptionOut]
    # CỐ Ý không có accepted_answers và explanation


class LessonOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    slug: str
    title: str
    lesson_type: str
    level: str | None
    objective: str | None
    position: int


class LessonPage(BaseModel):
    items: list[LessonOut]
    total: int
    limit: int
    offset: int