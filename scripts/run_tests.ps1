# Run tests script for Windows PowerShell

Write-Host "Running tests..." -ForegroundColor Green

# Activate virtual environment if exists
if (Test-Path "venv\Scripts\activate.ps1") {
    Write-Host "Activating virtual environment..." -ForegroundColor Yellow
    .\venv\Scripts\activate.ps1
}

# Run pytest
Write-Host "`nRunning pytest..." -ForegroundColor Cyan
pytest tests/ -v

# Run with coverage
Write-Host "`nRunning with coverage..." -ForegroundColor Cyan
pytest tests/ --cov=src --cov-report=term-missing --cov-report=html

Write-Host "`nTests completed! Check htmlcov/index.html for coverage report." -ForegroundColor Green

