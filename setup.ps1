# SMILE DENTAL BOOKING SYSTEM - QUICK SETUP SCRIPT (Windows)
# Run this script in PowerShell to set up the backend locally

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Smile Dental Backend - Setup Script" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

# Check if Python is installed
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python not found. Please install Python 3.8+" -ForegroundColor Red
    exit 1
}

# Navigate to backend folder
if (-not (Test-Path backend)) {
    New-Item -ItemType Directory -Name backend -Force | Out-Null
}
Set-Location backend

# Create virtual environment
Write-Host ""
Write-Host "Creating virtual environment..." -ForegroundColor Yellow
python -m venv venv

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& .\venv\Scripts\Activate.ps1

# Install dependencies
Write-Host "Installing dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt

# Create .env file from template
if (-not (Test-Path .env)) {
    Write-Host ""
    Write-Host "Creating .env file from template..." -ForegroundColor Yellow
    Copy-Item .env.example .env
    Write-Host "⚠️  IMPORTANT: Edit .env file and add your Twilio credentials:" -ForegroundColor Yellow
    Write-Host "   - TWILIO_ACCOUNT_SID"
    Write-Host "   - TWILIO_AUTH_TOKEN"
    Write-Host "   - TWILIO_PHONE_NUMBER"
    Write-Host "   - CLINIC_OWNER_PHONE"
}

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "✅ Setup Complete!" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. Edit backend\.env with your Twilio credentials" -ForegroundColor White
Write-Host "2. Run: python app.py" -ForegroundColor White
Write-Host "3. Backend will start at http://localhost:5000" -ForegroundColor White
Write-Host ""
Write-Host "If frontend is at http://localhost:3000," -ForegroundColor White
Write-Host "it will automatically connect to the backend." -ForegroundColor White
Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
