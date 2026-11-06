import random
import unicodedata
from dataclasses import dataclass, field


@dataclass(frozen=True)
class Kana:
    id: int
    char: str
    romaji: str
    alt: tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class Question:
    character_id: int
    char: str
    options: list[str] | None  # None khi mode == "typing"


def normalize(text: str) -> str:
    return unicodedata.normalize("NFKC", text).strip().lower()


def is_correct(kana: Kana, answer: str) -> bool:
    return normalize(answer) in {kana.romaji, *kana.alt}


def build_questions(
    lesson_chars: list[Kana],
    all_chars: list[Kana],
    mode: str,
    count: int = 10,
    n_options: int = 4,
    rng: random.Random | None = None,
) -> list[Question]:
    rng = rng or random.Random()
    picked = rng.sample(lesson_chars, min(count, len(lesson_chars)))
    questions: list[Question] = []

    for kana in picked:
        options = None
        if mode == "choice":
            # loại các chữ trùng phiên âm với đáp án đúng, và trùng nhau
            seen = {kana.romaji}
            pool = []
            for c in all_chars:
                if c.romaji not in seen:
                    seen.add(c.romaji)
                    pool.append(c.romaji)
            options = rng.sample(pool, min(n_options - 1, len(pool))) + [kana.romaji]
            rng.shuffle(options)
        questions.append(Question(kana.id, kana.char, options))

    return questions