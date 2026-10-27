# Dừng dự án JL. Chạy: .\stop.ps1
$root = $PSScriptRoot
docker compose -f "$root\docker-compose.yml" stop db
Write-Host "Đã dừng PostgreSQL. Đóng 2 cửa sổ backend/frontend bằng Ctrl+C rồi đóng cửa sổ." -ForegroundColor Green