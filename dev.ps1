# Khoi dong toan bo du an JL. Chay: .\dev.ps1
$root = $PSScriptRoot

# 1. Kiem tra Docker da san sang chua
docker info *> $null
if ($LASTEXITCODE -ne 0) {
    Write-Host "Docker chua chay. Hay mo Docker Desktop, doi khoi dong xong roi chay lai." -ForegroundColor Yellow
    exit 1
}

# 2. Bat PostgreSQL
Write-Host "Bat PostgreSQL..." -ForegroundColor Cyan
docker compose -f "$root\docker-compose.yml" up -d db
Start-Sleep -Seconds 3

# 3. Backend (cua so moi)
Write-Host "Bat backend (cong 8000)..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$root\backend'; .venv\Scripts\Activate.ps1; uvicorn app.main:app --reload --port 8000"

# 4. Frontend (cua so moi)
Write-Host "Bat frontend (cong 5173)..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$root\frontend'; npm run dev"

# 5. Mo trinh duyet sau vai giay
Start-Sleep -Seconds 5
Start-Process "http://localhost:5173"
Write-Host "Xong. API docs: http://localhost:8000/docs" -ForegroundColor Green