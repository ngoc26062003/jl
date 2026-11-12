# JL – Japanese Learning

Nền tảng học tiếng Nhật tương tác (Hiragana, Katakana, từ vựng và ngữ pháp N5).
Stack: Vue 3 + TypeScript / FastAPI / PostgreSQL.

## Chạy backend (local)

```bash
docker compose up -d                 # PostgreSQL
cd backend
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
python -m app.release                  # migrations + seed kana, vocabulary, and grammar
python -m pytest -v                  # test logic chấm bài
```

The N5 vocabulary deck contains 674 items and is available under **Practice → Từ vựng → N5**. Its Vietnamese glosses are machine-translated from English and may need review. The vocabulary data and its translations are licensed under [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/); see [the data notice](backend/app/data/NOTICE.md) for attribution and source details. JLPT levels are community approximations, not an official JLPT list.

The **Bài học** section includes 11 N5 grammar lessons on particles, with usage notes, examples, and four fill-in-the-blank exercises per lesson. The release seed is idempotent and publishes the lesson content and exercise answer keys.

## Deploy backend to Fly.io

Install `flyctl`, then set the `app` name and `primary_region` in `fly.toml` as needed. The Fly app `jl-japanese-learning` has already been created. Use the PostgreSQL connection string from your Supabase project's Connect dialog; do not use the local URL in `backend/.env`.

```bash
fly auth login
```

In PowerShell, enter the Supabase connection string at the masked prompt below. It is sent directly to Fly as a secret and is not written to the command history:

```powershell
$secureUrl = Read-Host "Supabase PostgreSQL URL" -AsSecureString
$pointer = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($secureUrl)
try {
	$databaseUrl = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($pointer)
	flyctl secrets set "DATABASE_URL=$databaseUrl" --app jl-japanese-learning
} finally {
	[Runtime.InteropServices.Marshal]::ZeroFreeBSTR($pointer)
	$databaseUrl = $null
	$secureUrl.Dispose()
}
```

The root `Dockerfile` packages FastAPI and its seed data. Fly runs database migrations and idempotently seeds kana, N5 vocabulary, and N5 grammar as a release command before deploying, then exposes `/health` for its service check. Once the Vercel frontend is deployed, set its exact origin (no trailing slash) as a Fly secret, then deploy:

```powershell
flyctl secrets set CORS_ORIGINS=https://your-project.vercel.app --app jl-japanese-learning
flyctl deploy --app jl-japanese-learning
```

Keep production database credentials in Fly secrets, not `.env` or `fly.toml`.

## Deploy frontend to Vercel

Import the repository into Vercel with `frontend` as the Root Directory. Vercel uses `npm run build` and `dist`; `frontend/vercel.json` enables client-side Vue Router routes. Set this environment variable for Production (and Preview if needed), replacing the hostname with your Fly app's public hostname:

```text
VITE_API_BASE_URL=https://jl-japanese-learning.fly.dev/api/v1
```

`frontend/.env.production` contains the public Fly API URL used by Vercel builds. For local frontend development, copy the value from `frontend/.env.example` into the ignored `frontend/.env`. The API URL is public and embedded in the built client.

## Tiến độ
- [x] Bước 1: logic chấm bài + test
- [x] Bước 2: models SQLAlchemy + migrations
- [x] Bước 3: seed dữ liệu N5 + luyện tập và trắc nghiệm
