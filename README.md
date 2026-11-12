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
# Add a random AUTH_SECRET_KEY (32+ characters) and, to create the initial admin, BOOTSTRAP_ADMIN_PASSWORD (12+ characters) to the ignored backend/.env
python -m app.release                  # migrations + seed kana, vocabulary, and grammar
python -m pytest -v                  # test logic chấm bài
```

The N5 vocabulary deck contains 674 items and is available under **Practice → Từ vựng → N5**. Its Vietnamese glosses are machine-translated from English and may need review. The vocabulary data and its translations are licensed under [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/); see [the data notice](backend/app/data/NOTICE.md) for attribution and source details. JLPT levels are community approximations, not an official JLPT list.

The **Bài học** section includes 11 N5 grammar lessons on particles, with usage notes, examples, and four fill-in-the-blank exercises per lesson. The release seed is idempotent and publishes the lesson content and exercise answer keys.

## Accounts, practice history, and admin

Learners can register with a username, email, and password, or use Google Sign-In. Lessons and practice require an account; the home page remains public. Passwords are Argon2-hashed, registration cannot assign admin permissions, and protected APIs verify short-lived bearer tokens and roles on the server. Tokens stay in memory and are not restored after a page reload, so a fresh page load requires signing in again. Missing login fields are rejected before looking up an account.

Completed practice runs are graded and stored by the API. A learner earns 1 star on the first practice day, then the current consecutive-day count in stars (2 on day two, 3 on day three); a missed calendar day resets the next practice to day one. The day boundary uses `Asia/Ho_Chi_Minh`. The admin dashboard shows active learners, correct/incorrect item totals, objective-score leaderboard, user streaks, role controls, and editable home-page images. Uploaded images are limited to 5 MB, decoded/re-encoded as WebP, and stored in PostgreSQL.

The account avatar menu includes profile details, password change for password-based accounts, a recent practice history and score chart, a 35-day activity calendar, and logout. Google-only accounts continue to manage sign-in through Google.

There is deliberately no built-in admin password. Set a strong `AUTH_SECRET_KEY` (at least 32 characters) as a Fly secret before deploying. `BOOTSTRAP_ADMIN_PASSWORD` (at least 12 characters) is optional for database migration, but required to create the reserved `admin` account; if configured later, deploy again to bootstrap the account. Do not use a short numeric password or commit secrets. Example PowerShell setup that keeps the initial admin password out of command history:

```powershell
$bytes = New-Object byte[] 48
$rng = [System.Security.Cryptography.RandomNumberGenerator]::Create()
$rng.GetBytes($bytes)
$authSecret = [Convert]::ToBase64String($bytes)
flyctl secrets set "AUTH_SECRET_KEY=$authSecret" --app jl-japanese-learning
[Array]::Clear($bytes, 0, $bytes.Length)
$authSecret = $null
$rng.Dispose()

$securePassword = Read-Host "Strong initial admin password (12+ characters)" -AsSecureString
$pointer = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($securePassword)
try {
    $bootstrapPassword = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($pointer)
    if ($bootstrapPassword.Length -lt 12) { throw "Password must contain at least 12 characters." }
    flyctl secrets set "BOOTSTRAP_ADMIN_PASSWORD=$bootstrapPassword" --app jl-japanese-learning
} finally {
    [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($pointer)
    $bootstrapPassword = $null
    $securePassword.Dispose()
}
```

For Google Sign-In, create a Google OAuth **Web application** client. Add the production frontend origin (for example `https://jl-flax.vercel.app`) and local development origin (`http://localhost:5173`) to its authorized JavaScript origins. Set the same client ID as Fly secret `GOOGLE_CLIENT_ID` and Vercel Production environment variable `VITE_GOOGLE_CLIENT_ID`, then redeploy both. Until configured, Google Sign-In is explicitly disabled.

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
