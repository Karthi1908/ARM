Write-Host "Starting Agentic Risk Manager Frontend (Next.js)..." -ForegroundColor Green
Set-Location -Path (Join-Path $PSScriptRoot "frontend")
npm run dev
