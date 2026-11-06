import pytest
from app.services.romaji import to_romaji


@pytest.mark.parametrize("kana,expected", [
    ("たべる", "taberu"), ("きょう", "kyou"), ("がっこう", "gakkou"),
    ("ラーメン", "raamen"), ("まっちゃ", "matcha"), ("ファイル", "fairu"),
    ("しんぶん", "shinbun"), ("じゅう", "juu"),
])
def test_to_romaji(kana, expected):
    assert to_romaji(kana) == expected