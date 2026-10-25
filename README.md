# JL – Japanese Learning

Nền tảng học tiếng Nhật tương tác (Hiragana, Katakana, ngữ pháp).
Stack: Vue 3 + TypeScript (sau) / FastAPI / PostgreSQL.

## Chạy backend (local)

```bash
docker compose up -d                 # PostgreSQL
cd backend
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
python -m pytest -v                  # test logic chấm bài
```

## Tiến độ
- [x] Bước 1: logic chấm bài + test
- [x] Bước 2: models SQLAlchemy (chưa có migration)
- [ ] Bước 3: seed Hiragana + API bài học
