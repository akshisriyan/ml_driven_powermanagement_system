from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import pandas as pd
import sqlite3
import joblib
import subprocess
import os
from ..utils.netlogo import run_netlogo_simulation

router = APIRouter()

class GridParams(BaseModel):
    house_growth_rate: float

@router.get("/grid-status")
def get_grid_status():
    try:
        conn = sqlite3.connect('database.db')
        df = pd.read_sql_query("SELECT * FROM grid_data ORDER BY tick DESC LIMIT 1", conn)
        conn.close()
        if df.empty:
            return {}
        return df.to_dict(orient='records')[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/simulate")
def run_simulation(params: GridParams):
    try:
        # Update NetLogo parameter
        with open('../../../simulation/power_grid.nlogo', 'r') as f:
            lines = f.readlines()
        for i, line in enumerate(lines):
            if line.startswith('set house-growth-rate'):
                lines[i] = f'set house-growth-rate {params.house_growth_rate}\n'
        with open('../../../simulation/power_grid.nlogo', 'w') as f:
            f.writelines(lines)

        # Run NetLogo simulation
        run_netlogo_simulation()

        # Store results in SQLite
        df = pd.read_csv('../../../simulation/grid_data.csv')
        conn = sqlite3.connect('database.db')
        df.to_sql('grid_data', conn, if_exists='append', index=False)
        conn.close()
        return {"status": "Simulation completed"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/forecast")
def get_forecast():
    try:
        svr = joblib.load('models/svr_model.pkl')
        scaler = joblib.load('models/scaler.pkl')
        arima = joblib.load('models/arima_model.pkl')

        # Get latest grid data
        conn = sqlite3.connect('database.db')
        df = pd.read_sql_query("SELECT * FROM grid_data ORDER BY tick DESC LIMIT 1", conn)
        conn.close()

        # SVR prediction
        X = df[['total_voltage', 'house_count']]
        X_scaled = scaler.transform(X)
        svr_pred = svr.predict(X_scaled)[0]

        # ARIMA forecast
        arima_pred = arima.forecast(steps=10).tolist()

        return {"svr_prediction": svr_pred, "arima_forecast": arima_pred}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))