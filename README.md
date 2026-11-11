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

The root `Dockerfile` packages only FastAPI. Fly runs `alembic upgrade head` as a release command before deploying and exposes `/health` for its service check. Once the Vercel frontend is deployed, set its exact origin (no trailing slash) as a Fly secret, then deploy:

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

Redeploy the frontend after changing environment variables. The API URL is embedded at build time.

## Tiến độ
- [x] Bước 1: logic chấm bài + test
- [x] Bước 2: models SQLAlchemy (chưa có migration)
- [ ] Bước 3: seed Hiragana + API bài học
