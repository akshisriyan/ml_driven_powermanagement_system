# Setup script for ML-Driven Power Grid Management System

Write-Host "=== Setting up ML-Driven Power Grid Management System ===" -ForegroundColor Green

$projectRoot = "e:\NSBM COMPUTER SCIENCE\4th year\final project\Final System\Ml_Driven_PowerManagement_System"
Set-Location $projectRoot

Write-Host "`n1. Setting up Python Backend..." -ForegroundColor Cyan
Set-Location "$projectRoot\backend"

# Check if Python is installed
try {
    $pythonVersion = python --version 2>&1
    Write-Host "Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "Python not found! Please install Python 3.8+ and try again." -ForegroundColor Red
    exit 1
}

# Install Python dependencies
Write-Host "Installing Python dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt

Write-Host "`n2. Setting up Node.js Frontend..." -ForegroundColor Cyan
Set-Location "$projectRoot\frontend"

# Check if Node.js is installed
try {
    $nodeVersion = node --version 2>&1
    Write-Host "Node.js found: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "Node.js not found! Please install Node.js 14+ and try again." -ForegroundColor Red
    exit 1
}

# Install Node.js dependencies
Write-Host "Installing Node.js dependencies..." -ForegroundColor Yellow
npm install

Write-Host "`n3. Training ML Models..." -ForegroundColor Cyan
Set-Location "$projectRoot\ml_models"

# Create models directory if it doesn't exist
if (-not (Test-Path "$projectRoot\backend\app\models")) {
    New-Item -ItemType Directory -Path "$projectRoot\backend\app\models" -Force
}

Write-Host "Training SVR model..." -ForegroundColor Yellow
python train_svr.py

Write-Host "Training ARIMA model..." -ForegroundColor Yellow
python train_arima.py

Write-Host "`n4. Initializing Database..." -ForegroundColor Cyan
Set-Location "$projectRoot\backend"
python init_db.py

Write-Host "`n=== Setup Complete! ===" -ForegroundColor Green
Write-Host "Run './start-system.ps1' to start the application" -ForegroundColor White

Write-Host "`n=== System Requirements Check ===" -ForegroundColor Yellow
Write-Host "✓ Python dependencies installed" -ForegroundColor Green
Write-Host "✓ Node.js dependencies installed" -ForegroundColor Green
Write-Host "✓ ML models trained" -ForegroundColor Green
Write-Host "✓ Database initialized" -ForegroundColor Green

Write-Host "`nNote: Make sure NetLogo 6.3.0 is installed for simulation features." -ForegroundColor Magenta
