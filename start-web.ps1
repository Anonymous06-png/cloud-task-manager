$ErrorActionPreference = "Stop"

Set-Location $PSScriptRoot

$python = ".\.venv\Scripts\python.exe"
$root = Join-Path $env:LOCALAPPDATA "CloudTaskManager\postgresql16"
$ctl = Join-Path $root "binaries\bin\pg_ctl.exe"
$ready = Join-Path $root "binaries\bin\pg_isready.exe"

# Cấu hình local, không ghi secret vào file
$env:SECRET_KEY = & $python -c "import secrets; print(secrets.token_urlsafe(48))"
$env:PGPASSFILE = Join-Path $env:LOCALAPPDATA "CloudTaskManager\pgpass.conf"
$env:DATABASE_URL = "postgresql://cloudtask_app@127.0.0.1:55432/cloudtask_dev"
$env:DJANGO_ENV = "local"
$env:DEBUG = "False"
$env:SECURE_SSL_REDIRECT = "False"
$env:ALLOWED_HOSTS = "localhost,127.0.0.1"

# Bật PostgreSQL nếu chưa chạy
& $ctl -D "$root\data" status 2>$null
if ($LASTEXITCODE -ne 0) {
    & $ctl -D "$root\data" -l "$root\server.log" -w start
    if ($LASTEXITCODE -ne 0) { throw "PostgreSQL startup failed" }
}

& $ready -h 127.0.0.1 -p 55432
if ($LASTEXITCODE -ne 0) { throw "PostgreSQL not ready" }

# Chuẩn bị static và bật Django
& $python manage.py collectstatic --noinput
if ($LASTEXITCODE -ne 0) { throw "collectstatic failed" }

$entryUrl = "http://127.0.0.1:8000/"
Write-Host "`nWebsite: $entryUrl" -ForegroundColor Green
$browserJob = Start-Job -ArgumentList $entryUrl -ScriptBlock {
    param($url)
    for ($attempt = 0; $attempt -lt 30; $attempt++) {
        try {
            $response = Invoke-WebRequest -Uri $url -UseBasicParsing -TimeoutSec 2
            if ($response.StatusCode -eq 200) {
                Start-Process $url
                return
            }
        } catch {
            Start-Sleep -Seconds 1
        }
    }
    Write-Warning "Server did not become ready; open $url manually."
}
try {
    & $python manage.py runserver 127.0.0.1:8000 --noreload
} finally {
    Stop-Job $browserJob
    Receive-Job $browserJob
    Remove-Job $browserJob
}