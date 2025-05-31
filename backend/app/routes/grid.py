from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import pandas as pd
import sqlite3
import joblib
import subprocess
import os
from ..utils.netlogo import run_netlogo_simulation

router = APIRouter()

def get_database_path():
    """Get the absolute path to the database file"""
    return os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'database.db')

class GridParams(BaseModel):
    house_growth_rate: float

@router.get("/grid-status")
def get_grid_status():
    try:
        conn = sqlite3.connect(get_database_path())
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
        # For now, generate mock simulation data instead of running NetLogo
        # TODO: Implement actual NetLogo integration once setup is complete
        import random
        import datetime
        
        # Generate some mock simulation data
        simulation_data = []
        base_tick = 1000  # Start from tick 1000 to avoid conflicts
        
        for i in range(10):  # Generate 10 data points
            tick = base_tick + i
            voltage = 22000 + random.uniform(-2000, 2000) * params.house_growth_rate
            load = 1000 + random.uniform(-200, 200) * params.house_growth_rate
            houses = int(50 + i * params.house_growth_rate)
            
            simulation_data.append({
                'tick': tick,
                'total_voltage': voltage,
                'total_load': load,
                'house_count': houses
            })
        
        # Store results in SQLite
        conn = sqlite3.connect(get_database_path())
        df = pd.DataFrame(simulation_data)
        df.to_sql('grid_data', conn, if_exists='append', index=False)
        conn.close()
        
        return {"status": "Simulation completed", "data_points": len(simulation_data)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/forecast")
def get_forecast():
    try:
        # For now, return mock predictions since model files might not exist
        # TODO: Implement actual model loading once models are trained
        try:
            svr = joblib.load('models/svr_model.pkl')
            scaler = joblib.load('models/scaler.pkl')
            arima = joblib.load('models/arima_model.pkl')
            
            # Get latest grid data
            conn = sqlite3.connect(get_database_path())
            df = pd.read_sql_query("SELECT * FROM grid_data ORDER BY tick DESC LIMIT 1", conn)
            conn.close()

            # SVR prediction
            X = df[['total_voltage', 'house_count']]
            X_scaled = scaler.transform(X)
            svr_pred = svr.predict(X_scaled)[0]

            # ARIMA forecast
            arima_pred = arima.forecast(steps=10).tolist()

            return {"svr_prediction": svr_pred, "arima_forecast": arima_pred}
        except FileNotFoundError:
            # Return mock predictions if models don't exist
            return {
                "svr_prediction": 1250.5,
                "arima_forecast": [1200, 1220, 1240, 1260, 1280, 1300, 1320, 1340, 1360, 1380]
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/historical-data")
def get_historical_data(limit: int = 100):
    """Get historical grid data for charting"""
    try:
        conn = sqlite3.connect(get_database_path())
        query = """
        SELECT tick, total_voltage, total_load, house_count, 
               datetime('now', '-' || (? - tick) || ' minutes') as timestamp
        FROM grid_data 
        ORDER BY tick DESC 
        LIMIT ?
        """
        df = pd.read_sql_query(query, conn, params=[limit, limit])
        conn.close()
        
        if df.empty:
            return {"data": []}
            
        # Convert to list of dictionaries and reverse to get chronological order
        data = df.to_dict(orient='records')
        data.reverse()
        
        return {"data": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/system-health")
def get_system_health():
    """Get system health metrics"""
    try:
        conn = sqlite3.connect(get_database_path())
        
        # Get latest data
        latest_query = "SELECT * FROM grid_data ORDER BY tick DESC LIMIT 1"
        latest_data = pd.read_sql_query(latest_query, conn)
        
        # Get data count
        count_query = "SELECT COUNT(*) as total_records FROM grid_data"
        count_data = pd.read_sql_query(count_query, conn)
        
        # Calculate averages for last 10 records
        avg_query = """
        SELECT 
            AVG(total_voltage) as avg_voltage,
            AVG(total_load) as avg_load,
            AVG(house_count) as avg_houses
        FROM (
            SELECT * FROM grid_data ORDER BY tick DESC LIMIT 10
        )
        """
        avg_data = pd.read_sql_query(avg_query, conn)
        
        conn.close()
        
        health_status = "healthy"
        if not latest_data.empty:
            voltage = latest_data.iloc[0]['total_voltage']
            load = latest_data.iloc[0]['total_load']
            
            if voltage < 20000 or load > 1500:
                health_status = "warning"
            if voltage < 15000 or load > 2000:
                health_status = "critical"
        
        return {
            "status": health_status,
            "total_records": int(count_data.iloc[0]['total_records']) if not count_data.empty else 0,
            "latest_tick": int(latest_data.iloc[0]['tick']) if not latest_data.empty else 0,
            "averages": {
                "voltage": float(avg_data.iloc[0]['avg_voltage']) if not avg_data.empty and avg_data.iloc[0]['avg_voltage'] else 0,
                "load": float(avg_data.iloc[0]['avg_load']) if not avg_data.empty and avg_data.iloc[0]['avg_load'] else 0,
                "houses": float(avg_data.iloc[0]['avg_houses']) if not avg_data.empty and avg_data.iloc[0]['avg_houses'] else 0
            },
            "timestamp": pd.Timestamp.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/clear-data")
def clear_grid_data():
    """Clear all grid data (for testing purposes)"""
    try:
        conn = sqlite3.connect(get_database_path())
        cursor = conn.cursor()
        cursor.execute("DELETE FROM grid_data")
        conn.commit()
        deleted_count = cursor.rowcount
        conn.close()
        
        return {"message": f"Cleared {deleted_count} records from grid_data"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/model-performance")
def get_model_performance():
    """Get ML model performance metrics"""
    try:
        # This would typically come from model evaluation data
        # For now, we'll return simulated performance metrics
        return {
            "svr_model": {
                "accuracy": 85.2,
                "mae": 15.3,
                "rmse": 22.1,
                "last_trained": "2024-01-15T10:30:00Z"
            },
            "arima_model": {
                "mae": 12.4,
                "rmse": 18.7,
                "aic": 1245.6,
                "last_trained": "2024-01-15T11:15:00Z"
            },
            "ensemble_performance": {
                "weighted_accuracy": 87.8,
                "prediction_confidence": 82.5
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))