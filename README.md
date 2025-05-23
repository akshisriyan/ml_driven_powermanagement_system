# ML-Driven Power Grid Management

![Project Status](https://img.shields.io/badge/status-in%20development-yellow)
![License](https://img.shields.io/badge/license-MIT-blue)

This is a final year project for NSBM Green University, Faculty of Computing, developed as part of the Computer Science degree program. The ML-Driven Power Grid Management System is designed to simulate, monitor, and predict power grid metrics using machine learning and agent-based modeling. It integrates a React-based frontend, a FastAPI backend, a NetLogo simulation, and machine learning models (SVR and ARIMA) to provide real-time grid status, run simulations, and forecast grid performance metrics such as voltage, load, and house count.

## Table of Contents
- [Project Overview](#project-overview)
- [Features](#features)
- [Architecture](#architecture)
- [Directory Structure](#directory-structure)
- [Prerequisites](#prerequisites)
- [Setup Instructions](#setup-instructions)
  - [Backend Setup](#backend-setup)
  - [Frontend Setup](#frontend-setup)
  - [Simulation Setup](#simulation-setup)
  - [ML Models Setup](#ml-models-setup)
- [Usage](#usage)
- [API Endpoints](#api-endpoints)
- [Contributing](#contributing)
- [License](#license)
- [Contact](#contact)

## Project Overview
The ML-Driven Power Grid Management System aims to address the challenges of modern power grid management by leveraging machine learning and simulation technologies. The system simulates a power grid with dynamic house growth, monitors key metrics (total voltage, total load, house count), and uses ML models to predict future grid states. The project is built with a modular architecture, allowing for easy integration of new features and scalability.

Key objectives:
- Simulate power grid dynamics using NetLogo’s agent-based modeling.
- Provide a user-friendly React interface to visualize grid status and simulation results.
- Predict grid metrics using SVR and ARIMA models.
- Store and retrieve grid data using a SQLite database.
- Expose APIs for real-time grid monitoring and simulation control via FastAPI.

## Features
- **Real-Time Grid Monitoring**: View current grid metrics (voltage, load, house count) via the frontend.
- **Dynamic Simulations**: Run NetLogo simulations with customizable parameters (e.g., house growth rate).
- **ML Predictions**: Forecast grid load using SVR and ARIMA models.
- **RESTful APIs**: Interact with the backend to retrieve grid status, run simulations, and get forecasts.
- **Cross-Platform**: Backend and simulation run on Windows, Linux, or macOS; frontend accessible via any modern browser.
- **Data Persistence**: Store simulation results in a SQLite database for analysis.

## Architecture
The system follows a client-server architecture with the following components:
- **Frontend**: A React application styled with Tailwind CSS, hosted at `http://localhost:3000`, communicates with the backend via REST APIs.
- **Backend**: A FastAPI server hosted at `http://localhost:8000`, handling API requests, database operations, and NetLogo simulation triggers.
- **Simulation**: A NetLogo model (`power_grid.nlogo`) simulates a power grid with houses, outputting data to CSV files.
- **Machine Learning**: SVR and ARIMA models predict grid metrics, trained using Python scripts and stored as `.pkl` files.
- **Database**: A SQLite database (`database.db`) stores simulation results (tick, total_voltage, total_load, house_count).

## Directory Structure
```
Ml_Driven_PowerManagement_System/
├── backend/
│   ├── app/
│   │   ├── main.py               # FastAPI application entry point
│   │   ├── models/              # ML model files (svr_model.pkl, arima_model.pkl, scaler.pkl)
│   │   ├── routes/
│   │   │   └── grid.py          # API routes for grid status, simulation, and forecasting
│   │   └── utils/
│   │       └── netlogo.py       # NetLogo simulation utilities
│   ├── requirements.txt          # Python dependencies
│   ├── schema.sql               # SQLite database schema
│   └── database.db              # SQLite database (excluded from Git)
├── frontend/
│   ├── src/
│   │   └── App.js               # Main React component
│   ├── package.json             # Node.js dependencies
│   └── tailwind.config.js       # Tailwind CSS configuration
├── simulation/
│   └── power_grid.nlogo         # NetLogo simulation model
├── ml_models/
│   ├── train_svr.py             # Script to train SVR model
│   └── train_arima.py           # Script to train ARIMA model
├── docs/
│   └── (documentation files)    # Project documentation
├── .gitignore                   # Git ignore file
└── README.md                    # Project README
```

## Prerequisites
- **Node.js**: Version 14 or higher (for frontend).
- **Python**: Version 3.8 or higher (for backend and ML models).
- **NetLogo**: Version 6.3.0 (for simulation).
- **SQLite**: For database operations.
- **Git**: For version control.
- **Operating System**: Windows, Linux, or macOS.
- **Browser**: Chrome, Firefox, or any modern browser for the frontend.

## Setup Instructions

### Backend Setup
1. Navigate to the backend directory:
   ```bash
   cd backend
   ```
2. Create a virtual environment (optional but recommended):
   ```bash
   python -m venv venv
   source venv/Scripts/activate  # Windows
   # or
   source venv/bin/activate     # Linux/macOS
   ```
3. Install dependencies:
   ```bash
   python -m pip install --upgrade pip
   python -m pip install -r requirements.txt
   ```
4. Initialize the SQLite database:
   ```bash
   sqlite3 database.db < schema.sql
   ```
   Or in PowerShell:
   ```powershell
   Get-Content schema.sql | sqlite3 database.db
   ```
5. Run the FastAPI server:
   ```bash
   python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```
   Access the API at `http://localhost:8000`.

### Frontend Setup
1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```
2. Install Node.js dependencies:
   ```bash
   npm install
   ```
3. Start the React development server:
   ```bash
   npm start
   ```
   Access the frontend at `http://localhost:3000`.

### Simulation Setup
1. Ensure NetLogo 6.3.0 is installed (download from [netlogoweb.org](https://www.netlogoweb.org)).
2. Verify the NetLogo CLI path in `backend/app/utils/netlogo.py` (default: `C:/Program Files/NetLogo 6.3.0/netlogo-headless.bat` on Windows).
3. The `simulation/power_grid.nlogo` file is included in the repository. Simulations are triggered via the backend API.

### ML Models Setup
1. Navigate to the ML models directory:
   ```bash
   cd ml_models
   ```
2. Run the training scripts to generate model files:
   ```bash
   python train_svr.py
   python train_arima.py
   ```
   This creates `svr_model.pkl`, `arima_model.pkl`, and `scaler.pkl` in `backend/app/models/`.
3. Replace sample data in `train_svr.py` and `train_arima.py` with your dataset for accurate predictions.

## Usage
1. Start the backend server (`http://localhost:8000`).
2. Start the frontend server (`http://localhost:3000`).
3. Use the frontend to:
   - View real-time grid status.
   - Run simulations by setting parameters (e.g., house growth rate).
   - View ML-based predictions for grid metrics.
4. Alternatively, interact with the backend via API calls (see [API Endpoints](#api-endpoints)).

## API Endpoints
The FastAPI backend exposes the following endpoints:
- **GET /**: Root endpoint, returns a welcome message.
  ```json
  {"message": "ML Driven Power Grid Management Backend"}
  ```
- **GET /grid-status**: Retrieve the latest grid metrics from the database.
  ```json
  {
    "tick": 100,
    "total_voltage": 2400.5,
    "total_load": 950.2,
    "house_count": 102
  }
  ```
- **POST /simulate**: Run a NetLogo simulation with specified parameters.
  ```json
  {
    "house_growth_rate": 0.02
  }
  ```
  Response:
  ```json
  {"status": "Simulation completed"}
  ```
- **GET /forecast**: Get ML-based predictions for grid metrics.
  ```json
  {
    "svr_prediction": 960.5,
    "arima_forecast": [950.1, 951.2, ...]
  }
  ```

Test endpoints using tools like Postman or `curl`:
```bash
curl http://localhost:8000/grid-status
```

## Contributing
Contributions are welcome! To contribute:
1. Fork the repository.
2. Create a feature branch (`git checkout -b feature/YourFeature`).
3. Commit changes (`git commit -m "Add YourFeature"`).
4. Push to the branch (`git push origin feature/YourFeature`).
5. Open a Pull Request.

Please follow the [Code of Conduct](CODE_OF_CONDUCT.md) and ensure tests pass before submitting.

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contact
- **Author**: Akshitha Sriyanjith
- **GitHub**: [Akshisriyan](https://github.com/Akshisriyan)
- **Email**: akshi.sriyan@example.com
- **Project Repository**: [ML-Driven-Power-Grid-Management](https://github.com/Akshisriyan/ML-Driven-Power-Grid-Management)

For issues or feature requests, please open an issue on the GitHub repository.