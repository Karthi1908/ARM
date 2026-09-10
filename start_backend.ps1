Write-Host "Starting Agentic Risk Manager Backend (FastAPI)..." -ForegroundColor Cyan
Set-Location -Path $PSScriptRoot

if (Test-Path ".\.venv\Scripts\python.exe") {
    & ".\.venv\Scripts\python.exe" -m uvicorn backend.src.main:app --host 127.0.0.1 --port 8000 --reload
} else {
    python -m uvicorn backend.src.main:app --host 127.0.0.1 --port 8000 --reload
}
