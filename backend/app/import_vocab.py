"""python -m app.import_vocab --level N5 --file data\\vocab_n5.csv
CSV (UTF-8): term,reading,meaning_vi[,group]. Không có cột group thì tự chia bộ theo --chunk."""
import argparse
import csv
import re

from app.db.session import SessionLocal
from app.seed_practice import upsert_deck, upsert_items
from app.services.romaji import to_romaji

KANA_ONLY = re.compile(r"^[\u3040-\u309F\u30A0-\u30FF\u30FC\s]+$")


def slugify(text: str) -> str:
    return re.sub(r"\W+", "-", text.strip().lower()).strip("-")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--level", required=True, choices=["N5", "N4", "N3", "N2", "N1"])
    ap.add_argument("--file", required=True)
    ap.add_argument("--chunk", type=int, default=25)
    args = ap.parse_args()

    with open(args.file, encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))

    groups: dict[str, list[dict]] = {}
    errors: list[str] = []
    auto = 0
    for n, r in enumerate(rows, start=2):  # dòng 1 là header
        term = (r.get("term") or "").strip()
        reading = (r.get("reading") or "").strip() or term
        if not term or not KANA_ONLY.match(reading):
            errors.append(f"dòng {n}: thiếu term hoặc reading không phải kana ({reading!r})")
            continue
        group = (r.get("group") or "").strip()
        if not group:
            group = f"Phần {auto // args.chunk + 1}"
            auto += 1
        groups.setdefault(group, []).append(dict(
            term=term, reading=reading, romaji=to_romaji(reading), romaji_alt=[],
            meaning_vi=(r.get("meaning_vi") or "").strip() or None, extra=None,
        ))

    with SessionLocal() as db:
        total = 0
        for pos, (group, items) in enumerate(groups.items()):
            deck = upsert_deck(
                db, slug=f"vocab-{args.level.lower()}-{slugify(group)}", category="vocab",
                level=args.level, title_jp=f"語彙 {args.level}",
                title_vi=f"Từ vựng {args.level} – {group}", position=pos,
            )
            total += upsert_items(db, deck, items)
        db.commit()

    print(f"Thêm {total} từ vào {len(groups)} bộ; bỏ qua {len(errors)} dòng lỗi")
    for e in errors[:20]:
        print("  -", e)


if __name__ == "__main__":
    main()