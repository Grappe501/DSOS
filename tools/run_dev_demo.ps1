# Start FastAPI with demo readiness flags (PowerShell, repo root).
# Usage: .\tools\run_dev_demo.ps1
# Optional: .\tools\run_dev_demo.ps1 -Port 8001

param([int]$Port = 8000)

$ErrorActionPreference = "Stop"
Set-Location (Split-Path $PSScriptRoot -Parent)

$env:MALONE_DEMO_MODE = "1"
$env:MALONE_DEMO_SAFE_RESPONSES = "1"
$env:MALONE_DEMO_LIMITED_SCOPE = "1"

Write-Host "Demo flags set: MALONE_DEMO_MODE, MALONE_DEMO_SAFE_RESPONSES, MALONE_DEMO_LIMITED_SCOPE" -ForegroundColor Cyan
Write-Host "Starting uvicorn on http://127.0.0.1:$Port ..." -ForegroundColor Cyan

python -m uvicorn app.main:app --host 127.0.0.1 --port $Port
