import pytest
from app.services.grading import is_correct


@pytest.mark.parametrize("answer,accepted,expected", [
    ("ka", ["ka"], True),
    ("  KA ", ["ka"], True),
    ("ｋａ", ["ka"], True),
    ("si", ["shi", "si"], True),
    ("shi", ["shi"], True),
    ("ti", ["chi"], False),
    ("か", ["か"], True),
    ("カ", ["か"], False),
    ("っ", ["つ"], False),
    ("", ["ka"], False),
    ("   ", ["ka"], False),
])
def test_is_correct(answer, accepted, expected):
    assert is_correct(answer, accepted) is expected
