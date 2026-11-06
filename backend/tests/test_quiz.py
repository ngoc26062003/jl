import random
from app.services.quiz import Kana, build_questions, is_correct

SHI = Kana(1, "し", "shi", ("si",))

def test_accepts_variants_and_whitespace():
    assert is_correct(SHI, " SI ")
    assert is_correct(SHI, "shi")
    assert not is_correct(SHI, "chi")

def test_choice_has_unique_options_with_correct_one():
    allk = [Kana(i, str(i), f"r{i}") for i in range(20)]
    qs = build_questions(allk[:3], allk, "choice", 3, rng=random.Random(0))
    for q in qs:
        assert len(q.options) == 4 and len(set(q.options)) == 4
        assert f"r{q.character_id}" in q.options

def test_typing_has_no_options():
    allk = [Kana(i, str(i), f"r{i}") for i in range(5)]
    assert build_questions(allk, allk, "typing", 2)[0].options is None