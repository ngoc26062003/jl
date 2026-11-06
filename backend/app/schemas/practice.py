from pydantic import BaseModel, ConfigDict, Field


class DeckOut(BaseModel):
    id: int
    category: str
    level: str | None
    slug: str
    title_jp: str
    title_vi: str
    item_count: int


class ItemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    deck_id: int
    term: str
    reading: str
    romaji: str
    romaji_alt: list[str] = Field(default_factory=list)
    meaning_vi: str | None = None
    extra: dict | None = None


class ItemsOut(BaseModel):
    items: list[ItemOut]
    distractors: list[ItemOut] = Field(default_factory=list)