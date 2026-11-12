from app.seed_grammar_n5 import GRAMMAR_LESSONS, validate_curriculum


def test_n5_grammar_curriculum_has_complete_lessons_and_exercises():
    validate_curriculum()

    assert len(GRAMMAR_LESSONS) == 11
    assert sum(len(lesson["questions"]) for lesson in GRAMMAR_LESSONS) == 44
    assert all(len(lesson["content"]["examples"]) >= 3 for lesson in GRAMMAR_LESSONS)


def test_every_grammar_exercise_has_one_answer_and_explanation():
    for lesson in GRAMMAR_LESSONS:
        for sentence, _, options, correct, explanation in lesson["questions"]:
            assert "（　）" in sentence
            assert options.count(correct) == 1
            assert explanation
