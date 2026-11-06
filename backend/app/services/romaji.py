_BASE_ROWS = {
    "あいうえお": ["a", "i", "u", "e", "o"], "かきくけこ": ["ka", "ki", "ku", "ke", "ko"],
    "がぎぐげご": ["ga", "gi", "gu", "ge", "go"], "さしすせそ": ["sa", "shi", "su", "se", "so"],
    "ざじずぜぞ": ["za", "ji", "zu", "ze", "zo"], "たちつてと": ["ta", "chi", "tsu", "te", "to"],
    "だぢづでど": ["da", "ji", "zu", "de", "do"], "なにぬねの": ["na", "ni", "nu", "ne", "no"],
    "はひふへほ": ["ha", "hi", "fu", "he", "ho"], "ばびぶべぼ": ["ba", "bi", "bu", "be", "bo"],
    "ぱぴぷぺぽ": ["pa", "pi", "pu", "pe", "po"], "まみむめも": ["ma", "mi", "mu", "me", "mo"],
    "やゆよ": ["ya", "yu", "yo"], "らりるれろ": ["ra", "ri", "ru", "re", "ro"],
    "わをん": ["wa", "wo", "n"], "ゔ": ["vu"], "ぁぃぅぇぉ": ["a", "i", "u", "e", "o"],
}
BASE = {ch: r for chars, roms in _BASE_ROWS.items() for ch, r in zip(chars, roms)}

_YOON = {"き": "ky", "し": "sh", "ち": "ch", "に": "ny", "ひ": "hy", "み": "my",
         "り": "ry", "ぎ": "gy", "び": "by", "ぴ": "py", "じ": "j", "ぢ": "j"}
COMBO = {k + small: pre + v for k, pre in _YOON.items() for small, v in zip("ゃゅょ", "auo")}
COMBO.update({"ふぁ": "fa", "ふぃ": "fi", "ふぇ": "fe", "ふぉ": "fo", "てぃ": "ti", "でぃ": "di",
              "しぇ": "she", "じぇ": "je", "ちぇ": "che", "うぃ": "wi", "うぇ": "we", "うぉ": "wo"})


def kata_to_hira(text: str) -> str:
    return "".join(chr(ord(c) - 0x60) if "ァ" <= c <= "ヴ" else c for c in text)


def to_romaji(text: str) -> str:
    s = kata_to_hira(text.strip())
    out: list[str] = []
    geminate = False
    i = 0
    while i < len(s):
        c, pair = s[i], s[i:i + 2]
        step = 1
        if c == "っ":
            geminate = True
            i += 1
            continue
        if pair in COMBO:
            r, step = COMBO[pair], 2
        elif c in BASE:
            r = BASE[c]
        elif c == "ー":
            r = out[-1][-1] if out else ""
        elif c.isspace() or c == "・":
            r = ""
        else:
            r = c
        if geminate and r:
            r = ("t" if r.startswith("ch") else r[0]) + r
            geminate = False
        out.append(r)
        i += step
    return "".join(out)