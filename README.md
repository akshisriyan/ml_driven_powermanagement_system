# 🔋 ML-Driven Power Grid Management System

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![React](https://img.shields.io/badge/React-18.2.0-blue.svg)](https://reactjs.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115.0-green.svg)](https://fastapi.tiangolo.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> An intelligent power grid management system using machine learning for real-time monitoring, voltage forecasting, and load prediction.

## 🌟 Overview

The ML-Driven Power Grid Management System is a comprehensive solution for monitoring and managing electrical power grids using advanced machine learning techniques. The system provides real-time data visualization, intelligent forecasting, and predictive analytics to optimize power distribution and ensure grid stability.

### 🎯 Key Features

- **🔍 Real-time Grid Monitoring** - Live visualization of voltage, load, and grid status
- **📈 ARIMA-based Voltage Forecasting** - Predict voltage trends for 1 hour to 24 hours
- **🤖 SVR Load Prediction** - Machine learning-powered load forecasting
- **📊 Interactive Dashboard** - Modern, responsive web interface with dark theme
- **📂 Data Management** - Excel file upload and CSV export capabilities
- **⚡ NetLogo Simulation Integration** - Grid simulation and modeling
- **🔄 Automated Data Processing** - Real-time data scaling and preprocessing
- **📱 Responsive Design** - Works on desktop, tablet, and mobile devices

### 🏗️ System Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Frontend      │    │     Backend      │    │   ML Models     │
│   (React)       │◄──►│   (FastAPI)      │◄──►│   (Sklearn)     │
│                 │    │                  │    │                 │
│ • Dashboard     │    │ • REST API       │    │ • ARIMA         │
│ • Charts        │    │ • Database       │    │ • SVR           │
│ • Controls      │    │ • ML Integration │    │ • Scaler        │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌──────────────────┐
                    │   NetLogo        │
                    │   Simulation     │
                    │                  │
                    │ • Grid Model     │
                    │ • Power Flow     │
                    │ • Load Simulation│
                    └──────────────────┘
```

## 🚀 Quick Start

### Prerequisites

Before setting up the project, ensure you have the following installed:

- **Python 3.8+** ([Download](https://python.org/downloads/))
- **Node.js 16+** ([Download](https://nodejs.org/))
- **Git** ([Download](https://git-scm.com/))
- **NetLogo 6.0+** (Optional, for simulation)

### 🔧 Installation

#### 1. Clone the Repository
```bash
git clone https://github.com/Akshisriyan/Ml_Driven_PowerManagement_System.git
cd Ml_Driven_PowerManagement_System
```

#### 2. Backend Setup

##### Create Python Virtual Environment
```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

##### Install Python Dependencies
```bash
pip install -r requirements.txt
```

##### Initialize Database and Train Models
```bash
# Initialize SQLite database
python init_db.py

# Train ML models (ARIMA, SVR, Scaler)
python train_models.py
```

#### 3. Frontend Setup

```bash
# Navigate to frontend directory
cd ../frontend

# Install Node.js dependencies
npm install

# Start development server
npm start
```

#### 4. Start the Application

##### Terminal 1 - Backend Server
```bash
cd backend
python -m app.main
```
Backend will run on: `http://localhost:5000`

##### Terminal 2 - Frontend Server
```bash
cd frontend
npm start
```
Frontend will run on: `http://localhost:3000` (or `http://localhost:3001` if 3000 is occupied)

### 🌐 Access the Application

Once both servers are running:
- **Dashboard**: Open `http://localhost:3000` in your browser
- **API Documentation**: Visit `http://localhost:5000/docs` for Swagger API docs

## 📁 Project Structure

```
Ml_Driven_PowerManagement_System/
├── 📂 backend/                 # Python FastAPI backend
│   ├── 📂 app/
│   │   ├── 📄 main.py         # FastAPI application entry point
│   │   ├── 📂 routes/         # API route handlers
│   │   ├── 📂 models/         # Data models
│   │   └── 📂 utils/          # Utility functions
│   ├── 📂 models/             # Trained ML model files (.pkl)
│   ├── 📄 database.db         # SQLite database
│   ├── 📄 requirements.txt    # Python dependencies
│   ├── 📄 init_db.py         # Database initialization
│   └── 📄 train_models.py    # ML model training
├── 📂 frontend/               # React frontend
│   ├── 📂 src/
│   │   ├── 📂 components/     # React components
│   │   ├── 📂 services/       # API service functions
│   │   ├── 📄 App.js         # Main React application
│   │   └── 📄 App.css        # Styling and themes
│   ├── 📂 public/            # Static assets
│   └── 📄 package.json       # Node.js dependencies
├── 📂 model_scripts/          # Standalone ML model Python files
│   ├── 📄 arima_model.py     # ARIMA forecasting implementation
│   ├── 📄 svr_model.py       # SVR prediction implementation
│   ├── 📄 scaler_model.py    # Data preprocessing implementation
│   ├── 📄 complete_demo.py   # Integrated model demonstration
│   └── 📄 README.md          # Model usage documentation
├── 📂 simulation/             # NetLogo simulation files
│   └── 📄 power_grid.nlogo   # Grid simulation model
├── 📂 docs/                   # Additional documentation
└── 📄 README.md              # This file
```

## 🔮 Machine Learning Models

### 1. ARIMA Model (Voltage Forecasting)
- **Purpose**: Time series forecasting for voltage prediction
- **Input**: Historical voltage data
- **Output**: Future voltage predictions with confidence intervals
- **Use Cases**: 1-hour to 24-hour voltage planning

### 2. SVR Model (Load Prediction)
- **Purpose**: Support Vector Regression for power load prediction
- **Input**: Voltage and house count (scaled)
- **Output**: Predicted power load
- **Features**: RBF kernel, confidence estimation

### 3. StandardScaler (Data Preprocessing)
- **Purpose**: Data normalization and feature scaling
- **Input**: Raw grid data (voltage, house count)
- **Output**: Normalized data for ML models
- **Features**: Transform and inverse transform capabilities

## 🖥️ Frontend Components

### Main Dashboard Components

- **📊 GridStatus**: Real-time grid monitoring cards
- **📈 Charts**: Interactive data visualization using Recharts
- **🎛️ SimulationControls**: NetLogo simulation interface
- **🔮 ModelPredictions**: ML model prediction displays
- **💊 SystemHealth**: Grid health monitoring
- **⚡ VoltageForecast**: ARIMA-based voltage forecasting
- **📂 DataManager**: Excel upload and CSV export functionality

### UI Features

- **🌙 Dark Theme**: Modern glassmorphic design with high contrast
- **📱 Responsive Layout**: Optimized for all device sizes
- **🔄 Real-time Updates**: Auto-refresh every 30 seconds
- **⚠️ Error Handling**: Comprehensive error boundaries
- **🎨 Interactive Charts**: Hover effects and data tooltips

## 🔌 API Endpoints

### Grid Data Endpoints
- `GET /grid-status` - Current grid status
- `GET /historical-data` - Historical grid data
- `GET /system-health` - System health metrics

### ML Model Endpoints
- `GET /forecast` - General forecast data
- `GET /voltage-forecast` - ARIMA voltage predictions
- `GET /forecast-summary` - Forecast summary statistics

### Data Management Endpoints
- `POST /upload-excel` - Upload Excel data files
- `GET /export-data` - Export data as CSV
- `GET /data-statistics` - Data summary statistics

### Simulation Endpoints
- `POST /simulate` - Run NetLogo simulation
- `GET /simulation-status` - Check simulation status

## ⚙️ Configuration

### Backend Configuration

Edit `backend/app/main.py` for:
- **Database settings**: SQLite database path
- **Model paths**: ML model file locations
- **API settings**: CORS, port configuration

### Frontend Configuration

Edit `frontend/src/services/api.js` for:
- **API base URL**: Backend server URL
- **Request timeouts**: API call timeout settings
- **Error handling**: Custom error messages

### Environment Variables

Create `.env` files for environment-specific settings:

#### Backend `.env`
```bash
DATABASE_URL=sqlite:///./database.db
MODEL_PATH=./models/
DEBUG=True
PORT=5000
```

#### Frontend `.env`
```bash
REACT_APP_API_URL=http://localhost:5000
REACT_APP_REFRESH_INTERVAL=30000
```

## 🧪 Testing

### Backend Testing
```bash
cd backend
python -m pytest tests/
```

### Frontend Testing
```bash
cd frontend
npm test
```

### Model Testing
```bash
cd model_scripts
python complete_demo.py
```

## 📊 Usage Examples

### Running Individual Models

#### ARIMA Voltage Forecasting
```python
from model_scripts.arima_model import ARIMAForecaster

forecaster = ARIMAForecaster()
forecast = forecaster.forecast_1_hour()
print(f"Next hour voltage: {forecast['forecast_values'][0]:.2f}V")
```

#### SVR Load Prediction
```python
from model_scripts.svr_model import SVRPredictor

predictor = SVRPredictor()
load = predictor.predict_load(voltage=22500, house_count=120)
print(f"Predicted load: {load:.2f} units")
```

#### Data Preprocessing
```python
from model_scripts.scaler_model import GridDataScaler

scaler = GridDataScaler()
normalized = scaler.normalize_grid_data(22500, 120)
print(f"Normalized data: {normalized[0]}")
```

### Complete Analysis
```python
from model_scripts.complete_demo import PowerGridAnalyzer

analyzer = PowerGridAnalyzer()
analysis = analyzer.comprehensive_analysis(voltage=22500, house_count=120)
analyzer.generate_report(voltage=22500, house_count=120)
```

## 🛠️ Development

### Adding New Features

1. **Backend**: Add new routes in `backend/app/routes/`
2. **Frontend**: Create components in `frontend/src/components/`
3. **Models**: Add new models in `model_scripts/`

### Code Style

- **Python**: Follow PEP 8 guidelines
- **JavaScript**: Use ESLint configuration
- **React**: Use functional components with hooks

### Database Migrations

To modify the database schema:
1. Update `backend/schema.sql`
2. Run `python init_db.py` to recreate tables
3. Retrain models if needed with `python train_models.py`

## 🚨 Troubleshooting

### Common Issues

#### Backend Won't Start
```bash
# Check Python version
python --version

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall

# Check database
python init_db.py
```

#### Frontend Build Errors
```bash
# Clear npm cache
npm cache clean --force

# Delete node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

#### Model Loading Errors
```bash
# Retrain models
cd backend
python train_models.py

# Check model files exist
ls models/
```

#### Port Conflicts
- Backend default: `5000` (change in `backend/app/main.py`)
- Frontend default: `3000` (automatically finds next available port)

### Performance Optimization

- **Database**: Add indexes for frequently queried columns
- **Frontend**: Implement lazy loading for large datasets
- **Models**: Cache predictions to reduce computation time
- **API**: Use pagination for large data responses

## 🤝 Contributing

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/AmazingFeature`)
3. **Commit** your changes (`git commit -m 'Add some AmazingFeature'`)
4. **Push** to the branch (`git push origin feature/AmazingFeature`)
5. **Open** a Pull Request

### Development Guidelines

- Write clear commit messages
- Add tests for new features
- Update documentation
- Follow existing code style
- Test across different browsers/devices

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👥 Authors

- **Akshisriyan** - *Initial work* - [Akshisriyan](https://github.com/Akshisriyan)

## 🙏 Acknowledgments

- **NSBM Green University** - Academic support and resources
- **FastAPI** - Modern Python web framework
- **React** - Frontend library
- **Scikit-learn** - Machine learning library
- **NetLogo** - Agent-based modeling platform
- **Recharts** - React charting library

## 📞 Support

For support, email your.email@example.com or create an issue on GitHub.

## 🔮 Future Enhancements

- [ ] Real-time data streaming with WebSockets
- [ ] Advanced ML models (LSTM, Transformer)
- [ ] Multi-grid management support
- [ ] Mobile application
- [ ] Cloud deployment with Docker
- [ ] Advanced analytics and reporting
- [ ] Integration with smart meters
- [ ] Predictive maintenance features

---

**⚡ Built with passion for sustainable energy management! 🌱**