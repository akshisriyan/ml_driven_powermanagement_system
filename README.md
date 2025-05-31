# 🔋 ML-Driven Power Management System

A comprehensive power grid management system featuring real-time monitoring, machine learning predictions, and interactive simulations with a beautiful blue-themed dashboard.

## 🌟 Features

- **🔍 Real-time Grid Monitoring** - Live voltage, load, and house count tracking
- **🤖 ML Predictions** - SVR and ARIMA models for load forecasting
- **🎮 NetLogo Simulation** - Interactive power grid simulation control
- **📊 Data Visualization** - Beautiful charts and real-time metrics
- **💎 Modern UI** - Glass morphism design with blue gradient theme
- **⚡ System Health** - Comprehensive monitoring and alerts

## 🛠️ System Requirements

### Software Prerequisites
- **Python 3.8+** - Backend API and ML models
- **Node.js 14+** - Frontend dashboard
- **NetLogo 6.3.0** - Grid simulation (optional)
- **PowerShell** - For running setup scripts (Windows)

### Hardware Requirements
- **RAM**: Minimum 4GB, Recommended 8GB+
- **Storage**: 2GB free space
- **Network**: Internet connection for package installation

## 🚀 Quick Start

### Option 1: Automated Setup (Recommended)

1. **Open PowerShell as Administrator** and navigate to the project directory:
   ```powershell
   cd "e:\NSBM COMPUTER SCIENCE\4th year\final project\Final System\Ml_Driven_PowerManagement_System"
   ```

2. **Run the automated setup** (first time only):
   ```powershell
   .\setup.ps1
   ```
   This script will:
   - ✅ Check Python 3.8+ and Node.js 14+ installation
   - ✅ Install all backend dependencies (FastAPI, uvicorn, scikit-learn, etc.)
   - ✅ Install all frontend dependencies (React, Recharts, Lucide React)
   - ✅ Train machine learning models (SVR and ARIMA)
   - ✅ Initialize the SQLite database

3. **Start the complete system**:
   ```powershell
   .\start-system.ps1
   ```
   This will:
   - 🚀 Start the FastAPI backend server on port 8000
   - 🚀 Start the React frontend server on port 3000
   - 🌐 Automatically open the dashboard in your browser

4. **Access the system**:
   - **Dashboard**: http://localhost:3000 (Beautiful blue-themed UI)
   - **Backend API**: http://localhost:8000 (REST API endpoints)
   - **API Docs**: http://localhost:8000/docs (Interactive Swagger documentation)

### Individual Component Commands

For manual control or troubleshooting, you can run components individually:

#### Backend Commands
```powershell
# Navigate to backend directory
cd backend

# Install dependencies (first time)
pip install fastapi uvicorn sqlalchemy scikit-learn pandas numpy statsmodels python-multipart

# Initialize database (first time)
python init_db.py

# Start backend server
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Alternative: Start with specific workers
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

#### Frontend Commands
```powershell
# Navigate to frontend directory
cd frontend

# Install dependencies (first time)
npm install

# Start development server
npm start

# Build for production
npm run build

# Start production server (after build)
npm run serve
```

#### ML Model Commands
```powershell
# Navigate to ML models directory
cd ml_models

# Train SVR model
python train_svr.py

# Train ARIMA model
python train_arima.py

# Train all models
python train_svr.py && python train_arima.py
```

#### Database Commands
```powershell
# Reinitialize database (will delete existing data)
cd backend
python init_db.py

# Backup database
copy database.db database_backup.db

# Restore database
copy database_backup.db database.db
```

#### Backend Setup

1. **Navigate to backend directory**:
   ```powershell
   cd backend
   ```

2. **Install Python dependencies**:
   ```powershell
   pip install -r requirements.txt
   ```

3. **Initialize the database**:
   ```powershell
   python init_db.py
   ```

4. **Train ML models**:
   ```powershell
   cd ..\ml_models
   python train_svr.py
   python train_arima.py
   ```

5. **Start the backend server**:
   ```powershell
   cd ..\backend
   python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

#### Frontend Setup

1. **Navigate to frontend directory**:
   ```powershell
   cd frontend
   ```

2. **Install Node.js dependencies**:
   ```powershell
   npm install
   ```

3. **Start the development server**:
   ```powershell
   npm start
   ```

## 📱 Usage

### Dashboard Features

1. **Grid Status Panel**
   - Real-time voltage, load, and house count
   - Status indicators with color-coded alerts
   - Trend analysis with visual indicators

2. **Charts & Visualization**
   - Voltage trend over time (Area chart)
   - Load vs House count comparison (Line chart)
   - ARIMA forecast predictions (Bar chart)
   - Power distribution by sector (Pie chart)

3. **Simulation Controls**
   - Adjust house growth rate (0.1% - 10%)
   - Run NetLogo simulations
   - Real-time parameter monitoring

4. **ML Model Predictions**
   - SVR (Support Vector Regression) predictions
   - ARIMA time series forecasting
   - Model performance metrics
   - 10-step forecast timeline

5. **System Health Monitoring**
   - Overall system status
   - Database metrics
   - Performance averages
   - System recommendations

### API Endpoints

#### Grid Management
- `GET /api/grid/current` - Get current grid status and metrics
- `GET /api/grid/historical` - Retrieve historical grid data with time range
- `GET /api/grid/forecast` - Get ML model predictions (SVR & ARIMA)
- `GET /api/grid/health` - System health and performance metrics
- `POST /api/grid/simulate` - Execute NetLogo simulation with parameters

#### Example API Usage
```powershell
# Test API endpoints using curl
curl http://localhost:8000/api/grid/current
curl http://localhost:8000/api/grid/historical?days=7
curl http://localhost:8000/api/grid/forecast
curl http://localhost:8000/api/grid/health

# Simulate with custom parameters
curl -X POST "http://localhost:8000/api/grid/simulate" -H "Content-Type: application/json" -d "{\"house_growth_rate\": 2.5, \"steps\": 100}"
```

#### Response Examples
```json
// GET /api/grid/current
{
  "voltage": 22500,
  "load": 875,
  "house_count": 120,
  "timestamp": "2025-05-31T10:30:00",
  "status": "normal"
}

// GET /api/grid/forecast
{
  "svr_prediction": [890, 905, 920, 935],
  "arima_forecast": [885, 900, 915, 930],
  "confidence_interval": [0.85, 0.92],
  "forecast_period": "next_4_hours"
}
```

## 🔧 Configuration

### Environment Variables
Create a `.env` file in the backend directory for custom configuration:
```env
# Database Configuration
DATABASE_URL=sqlite:///./database.db
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=0

# NetLogo Configuration
NETLOGO_PATH=C:\Program Files\NetLogo 6.3.0\NetLogo.exe
MODEL_PATH=../simulation/power_grid.nlogo
SIMULATION_TIMEOUT=300

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_WORKERS=4
DEBUG_MODE=true

# ML Model Configuration
MODEL_RETRAIN_INTERVAL=24  # hours
SVR_KERNEL=rbf
ARIMA_ORDER=(2,1,2)
FORECAST_HORIZON=10

# Security (for production)
SECRET_KEY=your-secret-key-here
CORS_ORIGINS=["http://localhost:3000"]
```

### Advanced Backend Configuration
```powershell
# Production deployment with multiple workers
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4 --log-level info

# Enable SSL for production
uvicorn app.main:app --host 0.0.0.0 --port 8000 --ssl-keyfile key.pem --ssl-certfile cert.pem

# Custom database configuration
$env:DATABASE_URL = "postgresql://user:password@localhost/powerdb"
python -m uvicorn app.main:app --reload
```

### Frontend Environment Configuration
Create a `.env` file in the frontend directory:
```env
# API Configuration
REACT_APP_API_URL=http://localhost:8000
REACT_APP_WS_URL=ws://localhost:8000/ws

# UI Configuration
REACT_APP_THEME=blue
REACT_APP_CHART_ANIMATION=true
REACT_APP_AUTO_REFRESH_INTERVAL=5000

# Features
REACT_APP_ENABLE_SIMULATION=true
REACT_APP_ENABLE_PREDICTIONS=true
REACT_APP_ENABLE_EXPORT=true

# Production Build
GENERATE_SOURCEMAP=false
INLINE_RUNTIME_CHUNK=false
```

### Simulation Parameters
Customize NetLogo simulation behavior:
```powershell
# Default parameters (can be modified via API)
$simulationParams = @{
    "house_growth_rate" = 2.0      # Percentage growth per step
    "voltage_target" = 22000       # Target voltage level
    "load_threshold" = 1200        # Maximum safe load (kW)
    "simulation_steps" = 100       # Number of simulation steps
    "random_seed" = 42             # For reproducible results
}

# Advanced simulation with custom parameters
curl -X POST "http://localhost:8000/api/grid/simulate" `
  -H "Content-Type: application/json" `
  -d ($simulationParams | ConvertTo-Json)
```

### ML Model Hyperparameters
Customize machine learning model settings in `ml_models/config.py`:
```python
# SVR Configuration
SVR_CONFIG = {
    'kernel': 'rbf',
    'C': 100,
    'gamma': 'scale',
    'epsilon': 0.1
}

# ARIMA Configuration  
ARIMA_CONFIG = {
    'order': (2, 1, 2),
    'seasonal_order': (1, 1, 1, 24),
    'trend': 'c'
}

# Training Configuration
TRAINING_CONFIG = {
    'test_size': 0.2,
    'cross_validation_folds': 5,
    'grid_search': True
}
```

## 🏗️ Project Structure

```
Ml_Driven_PowerManagement_System/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── main.py         # API entry point
│   │   ├── models/         # Data models
│   │   ├── routes/         # API endpoints
│   │   └── utils/          # NetLogo integration
│   ├── database.db        # SQLite database
│   ├── init_db.py         # Database initialization
│   └── requirements.txt   # Python dependencies
├── frontend/               # React dashboard
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── services/       # API services
│   │   └── App.js         # Main application
│   └── package.json       # Node.js dependencies
├── ml_models/             # Machine learning
│   ├── train_svr.py       # SVR model training
│   └── train_arima.py     # ARIMA model training
├── simulation/            # NetLogo simulation
│   └── power_grid.nlogo   # Grid simulation model
├── setup.ps1             # Automated setup script
└── start-system.ps1      # System startup script
```

## 🐛 Troubleshooting

### Common Issues & Solutions

#### Port Already in Use
```powershell
# Check what's using the ports
netstat -ano | findstr :3000
netstat -ano | findstr :8000

# Kill specific processes
taskkill /PID <PID_NUMBER> /F

# Alternative: Kill all Node.js and Python processes
taskkill /f /im node.exe
taskkill /f /im python.exe
```

#### Python Dependencies Issues
```powershell
# Upgrade pip and reinstall all dependencies
python -m pip install --upgrade pip
pip install -r requirements.txt --upgrade --force-reinstall

# If using virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

#### Node.js Package Issues
```powershell
# Clear npm cache and reinstall
npm cache clean --force
Remove-Item -Recurse -Force node_modules, package-lock.json
npm install

# If React build fails
npm install react-scripts@latest
npm audit fix
```

#### Database Connection Issues
```powershell
# Reset database completely
Remove-Item database.db
python init_db.py

# Check database file permissions
Get-Acl database.db | Format-List

# Verify database schema
sqlite3 database.db ".schema"
```

#### ML Model Training Failures
```powershell
# Install specific versions
pip install scikit-learn==1.3.0 pandas==2.0.3 numpy==1.24.3

# Clear cache and retrain
Remove-Item -Recurse __pycache__
python train_svr.py
python train_arima.py
```

#### NetLogo Integration Issues
```powershell
# Verify NetLogo installation
Test-Path "C:\Program Files\NetLogo 6.3.0\NetLogo.exe"

# Update NetLogo path in environment
$env:NETLOGO_PATH = "C:\Program Files\NetLogo 6.3.0\NetLogo.exe"

# Test simulation manually
cd simulation
# Open power_grid.nlogo in NetLogo GUI
```

#### Frontend Build Errors
```powershell
# Increase Node.js memory limit
$env:NODE_OPTIONS = "--max-old-space-size=4096"
npm start

# Build production version
npm run build
npx serve -s build -l 3000
```

#### System Performance Issues
```powershell
# Monitor system resources
Get-Process | Where-Object {$_.Name -like "*python*" -or $_.Name -like "*node*"} | Sort-Object CPU -Descending

# Check disk space
Get-PSDrive C

# Monitor memory usage
Get-Counter "\Memory\Available MBytes"
```

### Performance Optimization

- **Backend**: Increase worker count for production
- **Frontend**: Build for production: `npm run build`
- **Database**: Regular cleanup of old simulation data
- **Memory**: Monitor ML model memory usage

## 🚀 Deployment

### Local Production Deployment
```powershell
# Build frontend for production
cd frontend
npm run build

# Install production dependencies only
cd ..\backend
pip install -r requirements.txt --no-dev

# Start production servers
# Backend with multiple workers
Start-Process powershell -ArgumentList "-Command", "uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4"

# Frontend with optimized build
cd ..\frontend
npx serve -s build -l 3000
```

### Docker Deployment (Optional)
Create `Dockerfile` for backend:
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Create `docker-compose.yml`:
```yaml
version: '3.8'
services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    volumes:
      - ./backend/database.db:/app/database.db
    environment:
      - DATABASE_URL=sqlite:///./database.db
      
  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    depends_on:
      - backend
```

Deploy with Docker:
```powershell
# Build and start containers
docker-compose up -d

# View logs
docker-compose logs -f

# Stop containers
docker-compose down
```

### Windows Service Deployment
Install as Windows service:
```powershell
# Install NSSM (Non-Sucking Service Manager)
# Download from https://nssm.cc/download

# Install backend as service
nssm install "PowerGridBackend" "python" "-m uvicorn app.main:app --host 0.0.0.0 --port 8000"
nssm set "PowerGridBackend" AppDirectory "e:\...\backend"
nssm start "PowerGridBackend"

# Install frontend as service (production build)
nssm install "PowerGridFrontend" "npx" "serve -s build -l 3000"
nssm set "PowerGridFrontend" AppDirectory "e:\...\frontend"
nssm start "PowerGridFrontend"
```

### Cloud Deployment Options

#### Azure Deployment
```powershell
# Install Azure CLI
# https://docs.microsoft.com/en-us/cli/azure/install-azure-cli

# Login to Azure
az login

# Create resource group
az group create --name PowerGridRG --location eastus

# Deploy backend to Azure Container Instances
az container create --resource-group PowerGridRG --name powergrid-backend --image your-registry/powergrid-backend --ports 8000

# Deploy frontend to Azure Static Web Apps
az staticwebapp create --name powergrid-frontend --resource-group PowerGridRG --source https://github.com/your-repo
```

#### AWS Deployment
```powershell
# Install AWS CLI
# https://aws.amazon.com/cli/

# Configure AWS credentials
aws configure

# Deploy to AWS EC2
aws ec2 run-instances --image-id ami-0abcdef1234567890 --instance-type t2.micro --key-name your-key

# Deploy to AWS Elastic Beanstalk
eb init powergrid --platform python-3.9
eb create production
```

### Production Security Checklist
```powershell
# 1. Environment variables (never commit secrets)
# 2. HTTPS certificates
# 3. CORS configuration
# 4. Database security
# 5. API rate limiting
# 6. Input validation
# 7. Error handling
# 8. Logging configuration

# Example security headers
$headers = @{
    'X-Content-Type-Options' = 'nosniff'
    'X-Frame-Options' = 'DENY'
    'X-XSS-Protection' = '1; mode=block'
    'Strict-Transport-Security' = 'max-age=31536000; includeSubDomains'
}
```

## 🔄 Development & Testing

### Development Environment Setup
```powershell
# Create development branches
git checkout -b feature/new-ml-model
git checkout -b feature/ui-enhancement
git checkout -b bugfix/simulation-issue

# Install development dependencies
cd backend
pip install pytest pytest-asyncio httpx black flake8 mypy

cd ..\frontend
npm install --save-dev @testing-library/react @testing-library/jest-dom @testing-library/user-event
```

### Testing

#### Backend Testing
```powershell
# Navigate to backend directory
cd backend

# Run all tests
python -m pytest

# Run tests with coverage
python -m pytest --cov=app --cov-report=html

# Run specific test files
python -m pytest tests/test_api.py
python -m pytest tests/test_models.py -v

# Run tests with detailed output
python -m pytest -v -s

# Test specific endpoints
python -m pytest tests/test_grid_routes.py::test_get_current_status
```

Create `backend/tests/test_api.py`:
```python
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_get_current_grid_status():
    response = client.get("/api/grid/current")
    assert response.status_code == 200
    data = response.json()
    assert "voltage" in data
    assert "load" in data
    assert "house_count" in data

def test_get_health_check():
    response = client.get("/api/grid/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
```

#### Frontend Testing
```powershell
# Navigate to frontend directory
cd frontend

# Run all tests
npm test

# Run tests with coverage
npm test -- --coverage --watchAll=false

# Run specific test files
npm test -- GridStatus.test.js
npm test -- Charts.test.js

# Run tests in watch mode
npm test -- --watch

# Update snapshots
npm test -- --updateSnapshot
```

Create `frontend/src/components/__tests__/GridStatus.test.js`:
```javascript
import { render, screen } from '@testing-library/react';
import GridStatus from '../GridStatus';

test('renders grid status component', () => {
  const mockData = {
    voltage: 22500,
    load: 875,
    house_count: 120
  };
  
  render(<GridStatus data={mockData} />);
  expect(screen.getByText('22,500V')).toBeInTheDocument();
  expect(screen.getByText('875 kW')).toBeInTheDocument();
});
```

#### ML Model Testing
```powershell
# Test model training
cd ml_models
python -m pytest test_models.py

# Validate model performance
python train_svr.py --test-only
python train_arima.py --validate

# Test model predictions
python test_predictions.py
```

#### Integration Testing
```powershell
# Test complete system integration
.\test-integration.ps1

# Test API endpoints end-to-end
python -m pytest tests/test_integration.py

# Test database operations
python -m pytest tests/test_database.py

# Test NetLogo simulation
python -m pytest tests/test_simulation.py
```

### Code Quality & Formatting
```powershell
# Backend code formatting
cd backend
black app/ --line-length 88
flake8 app/ --max-line-length 88
mypy app/

# Frontend code formatting
cd ..\frontend
npx prettier --write "src/**/*.{js,jsx,css}"
npx eslint src/ --fix

# Run all quality checks
.\check-code-quality.ps1
```

### Performance Testing
```powershell
# Load testing with Apache Bench
ab -n 1000 -c 10 http://localhost:8000/api/grid/current

# Memory profiling
python -m memory_profiler backend/app/main.py

# Frontend performance testing
cd frontend
npm run build
npx lighthouse http://localhost:3000 --output html
```

### Adding New Features

#### 1. Backend API Endpoint
```powershell
# Create new route file
New-Item backend/app/routes/new_feature.py

# Add route to main.py
# from app.routes import new_feature
# app.include_router(new_feature.router, prefix="/api/new")

# Create tests
New-Item backend/tests/test_new_feature.py
```

#### 2. Frontend Component
```powershell
# Create component
New-Item frontend/src/components/NewComponent.js

# Create test file
New-Item frontend/src/components/__tests__/NewComponent.test.js

# Add to main App.js
# import NewComponent from './components/NewComponent';
```

#### 3. ML Model Enhancement
```powershell
# Create new model file
New-Item ml_models/train_new_model.py

# Add model integration
# Update backend/app/routes/grid.py to include new predictions

# Create model tests
New-Item ml_models/test_new_model.py
```

#### 4. Database Schema Changes
```powershell
# Update schema
# Modify backend/schema.sql

# Create migration script
New-Item backend/migrations/add_new_table.py

# Update models
# Modify backend/app/models/
```

## 📊 Monitoring & Maintenance

### Real-time System Monitoring
```powershell
# Monitor all system components
.\start-system.ps1  # Includes built-in monitoring

# Check backend health
Invoke-RestMethod http://localhost:8000/api/grid/health

# Monitor database size
Get-ChildItem database.db | Select-Object Name, Length, LastWriteTime

# Check system performance
Get-Counter -Counter "\Processor(_Total)\% Processor Time","\Memory\Available MBytes" -SampleInterval 5 -MaxSamples 10
```

### System Health Checks
```powershell
# Automated health check script
function Test-SystemHealth {
    Write-Host "=== System Health Check ===" -ForegroundColor Green
    
    # Check backend API
    try {
        $response = Invoke-RestMethod http://localhost:8000/api/grid/health -TimeoutSec 10
        Write-Host "✅ Backend API: Running" -ForegroundColor Green
    } catch {
        Write-Host "❌ Backend API: Down" -ForegroundColor Red
    }
    
    # Check frontend
    try {
        $response = Invoke-WebRequest http://localhost:3000 -TimeoutSec 10
        Write-Host "✅ Frontend: Running" -ForegroundColor Green
    } catch {
        Write-Host "❌ Frontend: Down" -ForegroundColor Red
    }
    
    # Check database
    if (Test-Path "backend\database.db") {
        Write-Host "✅ Database: Available" -ForegroundColor Green
    } else {
        Write-Host "❌ Database: Missing" -ForegroundColor Red
    }
    
    # Check ML models
    if (Test-Path "backend\app\models\svr_model.pkl") {
        Write-Host "✅ ML Models: Trained" -ForegroundColor Green
    } else {
        Write-Host "❌ ML Models: Missing" -ForegroundColor Red
    }
}

# Run health check
Test-SystemHealth
```

### Regular Maintenance Tasks
```powershell
# Daily maintenance script
function Start-DailyMaintenance {
    Write-Host "=== Daily Maintenance ===" -ForegroundColor Yellow
    
    # Backup database
    $backupName = "database_backup_$(Get-Date -Format 'yyyyMMdd').db"
    Copy-Item "backend\database.db" "backend\$backupName"
    Write-Host "✅ Database backed up: $backupName" -ForegroundColor Green
    
    # Clean old logs (if any)
    Get-ChildItem "*.log" -Recurse | Where-Object LastWriteTime -lt (Get-Date).AddDays(-7) | Remove-Item
    
    # Update ML model performance metrics
    cd ml_models
    python train_svr.py --validate-only
    python train_arima.py --validate-only
    cd ..
    
    Write-Host "✅ Daily maintenance completed" -ForegroundColor Green
}

# Weekly maintenance script
function Start-WeeklyMaintenance {
    Write-Host "=== Weekly Maintenance ===" -ForegroundColor Cyan
    
    # Update dependencies (check only)
    cd backend
    pip list --outdated
    
    cd ..\frontend
    npm outdated
    
    # Retrain ML models with latest data
    cd ..\ml_models
    python train_svr.py
    python train_arima.py
    
    # Clean old backups (keep last 4 weeks)
    Get-ChildItem "backend\database_backup_*.db" | Sort-Object LastWriteTime -Descending | Select-Object -Skip 28 | Remove-Item
    
    Write-Host "✅ Weekly maintenance completed" -ForegroundColor Green
}
```

### Performance Optimization
```powershell
# Optimize database
sqlite3 backend\database.db "VACUUM; REINDEX;"

# Clear Python cache
Get-ChildItem -Recurse -Force __pycache__ | Remove-Item -Recurse -Force

# Optimize Node.js performance
cd frontend
npm run build  # Create optimized production build
npx serve -s build -l 3000  # Serve optimized version

# Monitor resource usage
while ($true) {
    Clear-Host
    Write-Host "=== Resource Monitor ===" -ForegroundColor Green
    Get-Process | Where-Object {$_.Name -like "*python*" -or $_.Name -like "*node*"} | 
        Select-Object Name, CPU, WorkingSet, PagedMemorySize | 
        Sort-Object CPU -Descending | 
        Format-Table -AutoSize
    Start-Sleep 5
}
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👥 Authors

- **Your Name** - NSBM Computer Science Student
- **Project Supervisor** - Faculty Member

## 🆘 Support

For technical support or questions:
- Create an issue in the repository
- Contact the development team
- Check the troubleshooting section above

---

**Note**: This system is designed for educational and research purposes. For production deployment, additional security and scalability measures should be implemented.