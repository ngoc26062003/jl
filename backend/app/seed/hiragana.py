"""Nạp Hiragana vào DB. Chạy lại nhiều lần an toàn (bỏ qua bài đã có).
Chạy từ thư mục backend/:  python -m app.seed.hiragana
"""
import random

from sqlalchemy import select

from app.db.session import SessionLocal
from app.models import AcceptedAnswer, Category, Lesson, Question, QuestionOption
from app.seed.hiragana_data import ROWS


def seed() -> None:
    rng = random.Random(42)  # cố định để kết quả lặp lại được
    all_primary = [readings[0] for _, _, items in ROWS for _, readings in items]

    with SessionLocal() as db:
        category = db.scalar(select(Category).where(Category.slug == "hiragana"))
        if category is None:
            category = Category(slug="hiragana", name="Hiragana")
            db.add(category)
            db.flush()

        for pos, (key, title, items) in enumerate(ROWS, start=1):
            slug = f"hiragana-{key}"
            if db.scalar(select(Lesson.id).where(Lesson.slug == slug)):
                continue

            lesson = Lesson(
                category_id=category.id, slug=slug, title=title,
                lesson_type="kana", level=None,
                objective="Nhận biết và đọc đúng các ký tự Hiragana trong hàng này.",
                status="published", position=pos,
            )
            db.add(lesson)
            db.flush()

            q_pos = 0
            for char, readings in items:
                correct = readings[0]

                # Trắc nghiệm: ký tự -> chọn cách đọc
                mc = Question(
                    lesson_id=lesson.id, question_type="multiple_choice",
                    prompt={"text": "Chọn cách đọc đúng của ký tự sau", "character": char},
                    explanation=f"「{char}」đọc là “{correct}”.",
                    position=q_pos, difficulty=1,
                )
                db.add(mc)
                db.flush()
                q_pos += 1

                texts = [correct] + rng.sample([r for r in all_primary if r != correct], 3)
                rng.shuffle(texts)
                for t in texts:
                    db.add(QuestionOption(question_id=mc.id, text=t, is_correct=(t == correct)))

                # Nhập bàn phím: ký tự -> gõ romaji
                ty = Question(
                    lesson_id=lesson.id, question_type="typing",
                    prompt={"text": "Nhập cách đọc (romaji) của ký tự sau", "character": char},
                    explanation=f"「{char}」đọc là “{correct}”.",
                    position=q_pos, difficulty=1,
                )
                db.add(ty)
                db.flush()
                q_pos += 1

                for r in readings:
                    db.add(AcceptedAnswer(question_id=ty.id, text=r))

        db.commit()


if __name__ == "__main__":
    seed()
    print("Seed Hiragana xong.")