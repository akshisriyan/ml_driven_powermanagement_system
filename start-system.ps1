# ML-Driven Power Grid Management System
# Complete startup and run script

Write-Host "=== ML-Driven Power Grid Management System ===" -ForegroundColor Green
Write-Host "Starting system components..." -ForegroundColor Yellow

# Change to project root directory
$projectRoot = "e:\NSBM COMPUTER SCIENCE\4th year\final project\Final System\Ml_Driven_PowerManagement_System"
Set-Location $projectRoot

# Function to check if a port is in use
function Test-Port {
    param($Port)
    $connection = Test-NetConnection -ComputerName localhost -Port $Port -InformationLevel Quiet -WarningAction SilentlyContinue
    return $connection
}

Write-Host "`n1. Initializing Database..." -ForegroundColor Cyan
Set-Location "$projectRoot\backend"
python init_db.py

Write-Host "`n2. Starting Backend Server..." -ForegroundColor Cyan
if (Test-Port 8000) {
    Write-Host "Port 8000 is already in use. Please stop any existing backend server." -ForegroundColor Red
} else {
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$projectRoot\backend'; python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload" -WindowStyle Normal
    Write-Host "Backend server starting on http://localhost:8000" -ForegroundColor Green
    Start-Sleep 3
}

Write-Host "`n3. Starting Frontend Development Server..." -ForegroundColor Cyan
Set-Location "$projectRoot\frontend"
if (Test-Port 3000) {
    Write-Host "Port 3000 is already in use. Please stop any existing frontend server." -ForegroundColor Red
} else {
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$projectRoot\frontend'; npm start" -WindowStyle Normal
    Write-Host "Frontend server starting on http://localhost:3000" -ForegroundColor Green
    Start-Sleep 3
}

Write-Host "`n=== System Status ===" -ForegroundColor Green
Write-Host "Backend API: http://localhost:8000" -ForegroundColor White
Write-Host "Frontend Dashboard: http://localhost:3000" -ForegroundColor White
Write-Host "API Documentation: http://localhost:8000/docs" -ForegroundColor White

Write-Host "`n=== Available Features ===" -ForegroundColor Yellow
Write-Host "✓ Real-time grid monitoring" -ForegroundColor White
Write-Host "✓ NetLogo simulation control" -ForegroundColor White
Write-Host "✓ ML predictions (SVR & ARIMA)" -ForegroundColor White
Write-Host "✓ Historical data visualization" -ForegroundColor White
Write-Host "✓ System health monitoring" -ForegroundColor White

Write-Host "`nPress any key to open the dashboard in your browser..." -ForegroundColor Magenta
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

# Open browser to dashboard
Start-Process "http://localhost:3000"

Write-Host "`nSystem is now running! Close this window to stop monitoring." -ForegroundColor Green
Write-Host "Note: Backend and Frontend servers will continue running in separate windows." -ForegroundColor Yellow

# Keep the script running
while ($true) {
    Start-Sleep 10
    if (-not (Test-Port 8000)) {
        Write-Host "Backend server appears to be down!" -ForegroundColor Red
    }
    if (-not (Test-Port 3000)) {
        Write-Host "Frontend server appears to be down!" -ForegroundColor Red
    }
}
