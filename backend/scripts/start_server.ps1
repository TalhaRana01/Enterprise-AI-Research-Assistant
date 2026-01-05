# Start FastAPI server script

Write-Host "Starting AI Research Assistant API Server..." -ForegroundColor Green

# Activate virtual environment if exists (check root level)
if (Test-Path "..\venv\Scripts\activate.ps1") {
    Write-Host "Activating virtual environment..." -ForegroundColor Yellow
    ..\venv\Scripts\activate.ps1
} elseif (Test-Path "venv\Scripts\activate.ps1") {
    Write-Host "Activating virtual environment..." -ForegroundColor Yellow
    .\venv\Scripts\activate.ps1
}

# Check if .env file exists
if (-not (Test-Path ".env")) {
    Write-Host "Warning: .env file not found!" -ForegroundColor Yellow
    Write-Host "Please create .env file with required configuration." -ForegroundColor Yellow
}

# Start server
Write-Host "`nStarting server on http://localhost:8000" -ForegroundColor Cyan
Write-Host "API Docs: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host "Press Ctrl+C to stop the server`n" -ForegroundColor Yellow

uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload

