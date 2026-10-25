"""Chấm câu trả lời dạng nhập. Hàm thuần, không phụ thuộc DB nên dễ test."""
import unicodedata


def normalize_answer(text: str, *, case_sensitive: bool = False) -> str:
    # NFKC: ｋａ (full-width) -> ka, khoảng trắng full-width -> thường.
    # NFKC KHÔNG đổi か thành カ và không đổi つ thành っ, nên vẫn phân biệt được.
    s = unicodedata.normalize("NFKC", text)
    s = "".join(s.split())  # bỏ mọi khoảng trắng
    return s if case_sensitive else s.casefold()


def is_correct(
    user_answer: str,
    accepted: list[str],
    *,
    case_sensitive: bool = False,
) -> bool:
    given = normalize_answer(user_answer, case_sensitive=case_sensitive)
    if not given:
        return False
    return any(
        given == normalize_answer(a, case_sensitive=case_sensitive)
        for a in accepted
    )
