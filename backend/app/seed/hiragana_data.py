"""Dữ liệu Hiragana cơ bản (46 ký tự), nhóm theo hàng.
Mỗi ký tự: (ký tự, [cách đọc romaji chấp nhận]). Phần tử đầu là cách đọc chính (Hepburn).
"""

ROWS: list[tuple[str, str, list[tuple[str, list[str]]]]] = [
    ("a", "Hiragana – hàng あ (a, i, u, e, o)",
     [("あ", ["a"]), ("い", ["i"]), ("う", ["u"]), ("え", ["e"]), ("お", ["o"])]),
    ("ka", "Hiragana – hàng か (ka, ki, ku, ke, ko)",
     [("か", ["ka"]), ("き", ["ki"]), ("く", ["ku"]), ("け", ["ke"]), ("こ", ["ko"])]),
    ("sa", "Hiragana – hàng さ (sa, shi, su, se, so)",
     [("さ", ["sa"]), ("し", ["shi", "si"]), ("す", ["su"]), ("せ", ["se"]), ("そ", ["so"])]),
    ("ta", "Hiragana – hàng た (ta, chi, tsu, te, to)",
     [("た", ["ta"]), ("ち", ["chi", "ti"]), ("つ", ["tsu", "tu"]), ("て", ["te"]), ("と", ["to"])]),
    ("na", "Hiragana – hàng な (na, ni, nu, ne, no)",
     [("な", ["na"]), ("に", ["ni"]), ("ぬ", ["nu"]), ("ね", ["ne"]), ("の", ["no"])]),
    ("ha", "Hiragana – hàng は (ha, hi, fu, he, ho)",
     [("は", ["ha"]), ("ひ", ["hi"]), ("ふ", ["fu", "hu"]), ("へ", ["he"]), ("ほ", ["ho"])]),
    ("ma", "Hiragana – hàng ま (ma, mi, mu, me, mo)",
     [("ま", ["ma"]), ("み", ["mi"]), ("む", ["mu"]), ("め", ["me"]), ("も", ["mo"])]),
    ("ya", "Hiragana – hàng や (ya, yu, yo)",
     [("や", ["ya"]), ("ゆ", ["yu"]), ("よ", ["yo"])]),
    ("ra", "Hiragana – hàng ら (ra, ri, ru, re, ro)",
     [("ら", ["ra"]), ("り", ["ri"]), ("る", ["ru"]), ("れ", ["re"]), ("ろ", ["ro"])]),
    ("wa", "Hiragana – hàng わ (wa, wo, n)",
     [("わ", ["wa"]), ("を", ["wo", "o"]), ("ん", ["n"])]),
]