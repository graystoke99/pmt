$ErrorActionPreference = "Stop"

Set-Location (Join-Path $PSScriptRoot "..")
docker compose up --build -d

Write-Host "Frontend: http://localhost:3000"
Write-Host "Backend:  http://localhost:8000"