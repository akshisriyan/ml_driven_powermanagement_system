from fastapi import APIRouter, HTTPException, UploadFile, File
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import pandas as pd
import numpy as np
import sqlite3
import joblib
import subprocess
import os
import datetime
import warnings
import io
from ..utils.netlogo import run_netlogo_simulation, backfill_zone_metrics_for_recent

# Try to import statsmodels, if not available, provide fallback
try:
    from statsmodels.tsa.arima.model import ARIMA
    STATSMODELS_AVAILABLE = True
except ImportError:
    STATSMODELS_AVAILABLE = False
    print("Warning: statsmodels not available. ARIMA forecasting will be limited.")

warnings.filterwarnings('ignore')

router = APIRouter()

class GridParams(BaseModel):
    house_growth_rate: float | None = None
    temperature: float = 25.0
    humidity: float = 50.0
    solar_intensity: float = 500.0
    wind_speed: float = 5.0
    peak_hours: bool = False
    steps: int = 100
    houses: int = 120
    voltage: float = 220  # Use realistic 220V instead of 22500V

def get_database_path():
    """Get the absolute path to the database file"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    backend_dir = os.path.dirname(os.path.dirname(current_dir))
    return os.path.join(backend_dir, 'database.db')

def get_models_path():
    """Get the absolute path to the models directory"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    backend_dir = os.path.dirname(os.path.dirname(current_dir))
    return os.path.join(backend_dir, 'models')

@router.get("/grid-status")
def get_grid_status():
    try:
        conn = sqlite3.connect(get_database_path())
        df = pd.read_sql_query("SELECT * FROM grid_data ORDER BY tick DESC LIMIT 1", conn)
        conn.close()
        if df.empty:
            return {}
        
        # Convert to dict and apply voltage scaling
        data = df.to_dict(orient='records')[0]
        
        # Scale voltage to realistic 220V range if it's in 22000V range
        if 'total_voltage' in data and data['total_voltage'] > 1000:
            data['total_voltage'] = round(data['total_voltage'] / 100, 2)
            
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/system-health")
def get_system_health():
    try:
        conn = sqlite3.connect(get_database_path())

        # Get total record count
        total_count = pd.read_sql_query("SELECT COUNT(*) as count FROM grid_data", conn)['count'].iloc[0]

        # Get latest record
        latest_df = pd.read_sql_query("SELECT * FROM grid_data ORDER BY tick DESC LIMIT 1", conn)

        # Get averages (house_count removed; system uses zones)
        avg_df = pd.read_sql_query("SELECT AVG(total_voltage) as avg_voltage, AVG(total_load) as avg_load FROM grid_data", conn)

        conn.close()

        if latest_df.empty:
            return {
                "status": "warning",
                "total_records": 0,
                "latest_tick": 0,
                "averages": {"voltage": 0, "load": 0},
                "timestamp": pd.Timestamp.now().isoformat()
            }

        # Determine system health status
        avg_voltage = avg_df['avg_voltage'].iloc[0]
        avg_load = avg_df['avg_load'].iloc[0]
        
        # Scale voltage to realistic 220V range if it's in 22000V range
        if avg_voltage > 1000:
            avg_voltage = avg_voltage / 100  # Convert from 22000V to 220V range
            
        status = "healthy"
        
        # Updated thresholds for 220V range
        if avg_voltage < 200 or avg_load > 1200:
            status = "warning"
        if avg_voltage < 180 or avg_load > 1500:
            status = "critical"
        
        # Read generator setting
        try:
            sconn = sqlite3.connect(get_database_path())
            scur = sconn.cursor()
            scur.execute("SELECT value FROM settings WHERE key='generator_enabled'")
            srow = scur.fetchone()
            sconn.close()
            generator_enabled = bool(srow and str(srow[0]) == '1')
        except Exception:
            generator_enabled = False

        # Calculate temperature based on load, time of day, and last simulation parameters
        import datetime
        current_hour = datetime.datetime.now().hour
        base_temp = 25.0
        
        # Try to get last simulation temperature from settings
        try:
            sconn = sqlite3.connect(get_database_path())
            scur = sconn.cursor()
            scur.execute("SELECT value FROM settings WHERE key='last_simulation_temperature'")
            temp_row = scur.fetchone()
            if temp_row:
                base_temp = float(temp_row[0])
            sconn.close()
        except Exception:
            pass
        
        # Simulate temperature variation based on load and time of day
        load_impact = (avg_load / 1000) * 3  # Higher load increases temperature
        time_impact = 3 * np.sin((current_hour - 6) * np.pi / 12) if 6 <= current_hour <= 18 else -2
        temperature = base_temp + load_impact + time_impact + np.random.normal(0, 1.5)  # Add some variation
        temperature = max(15, min(45, temperature))  # Clamp between 15-45°C
        
        # Calculate efficiency based on voltage stability, load, and temperature
        voltage_efficiency = 100 - abs(220 - avg_voltage) * 0.8  # Penalty for voltage deviation
        load_efficiency = 100 - max(0, (avg_load - 800) * 0.03)  # Penalty for high load
        temp_efficiency = 100 - max(0, (temperature - 35) * 2)  # Penalty for high temperature
        overall_efficiency = min(100, max(60, (voltage_efficiency + load_efficiency + temp_efficiency) / 3))
        
        # Convert load to percentage (assuming max load around 1500)
        load_percentage = min(100, (avg_load / 1500) * 100)

        # Determine system status based on multiple factors
        status = "healthy"
        if avg_voltage < 200 or avg_load > 1200 or temperature > 35:
            status = "warning"
        if avg_voltage < 180 or avg_load > 1500 or temperature > 40:
            status = "critical"
        
        # Convert load to percentage (assuming max load around 1500)
        load_percentage = min(100, (avg_load / 1500) * 100)

        # Recommend action
        recommended_action = None
        if status in ("warning", "critical") and not generator_enabled:
            recommended_action = "enable_generator"

        return {
            "status": status,
            "voltage": float(avg_voltage),
            "temperature": float(round(temperature, 1)),
            "load": float(round(load_percentage, 1)),
            "generatorEnabled": generator_enabled,
            "efficiency": float(round(overall_efficiency, 1)),
            "lastUpdate": pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S'),
            "total_records": int(total_count),
            "latest_tick": int(latest_df['tick'].iloc[0]),
            "averages": {
                "voltage": float(avg_voltage),
                "load": float(avg_df['avg_load'].iloc[0])
            },
            "timestamp": pd.Timestamp.now().isoformat(),
            "generator": {"enabled": generator_enabled},
            "recommended_action": recommended_action
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/historical-data")
def get_historical_data(limit: int = 50):
    try:
        conn = sqlite3.connect(get_database_path())
        df = pd.read_sql_query(f"SELECT * FROM grid_data ORDER BY tick DESC LIMIT {limit}", conn)
        conn.close()
        
        if df.empty:
            return []
        
        # Convert to list of dictionaries and reverse to get chronological order
        data = df.to_dict(orient='records')
        
        # Apply voltage scaling to each record
        for record in data:
            if 'total_voltage' in record and record['total_voltage'] and record['total_voltage'] > 1000:
                record['total_voltage'] = round(record['total_voltage'] / 100, 2)
        
        return list(reversed(data))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/simulate")
def run_simulation(params: GridParams):
    try:
        # Resolve paths
        current_dir = os.path.dirname(os.path.abspath(__file__))
        backend_dir = os.path.dirname(os.path.dirname(current_dir))
        project_dir = os.path.dirname(backend_dir)
        sim_dir = os.path.join(project_dir, 'simulation')
        nlogo_path = os.path.join(sim_dir, 'power_grid.nlogo')
        csv_path = os.path.join(sim_dir, 'grid_data.csv')

        # Update NetLogo parameter if model file exists
        try:
            if os.path.exists(nlogo_path):
                with open(nlogo_path, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = f.readlines()
                for i, line in enumerate(lines):
                    if line.strip().startswith('set house-growth-rate'):
                        lines[i] = f'set house-growth-rate {params.house_growth_rate}\n'
                with open(nlogo_path, 'w', encoding='utf-8') as f:
                    f.writelines(lines)
        except Exception:
            pass

        # Run NetLogo simulation; pass environment parameters to synthetic fallback
        env = {
            'temperature': params.temperature, 
            'humidity': params.humidity, 
            'solar_intensity': params.solar_intensity,
            'wind_speed': params.wind_speed,
            'peak_hours': params.peak_hours
        }
        try:
            run_netlogo_simulation(env_params=env)
        except Exception as e:
            print(f"Simulation error: {e}")
            # If NetLogo not available, call synthetic generator directly with env params
            from ..utils.netlogo import generate_synthetic_data
            generate_synthetic_data(env_params=env)
        
        # Store simulation parameters for system health calculations
        try:
            sconn = sqlite3.connect(get_database_path())
            scur = sconn.cursor()
            scur.execute("INSERT OR REPLACE INTO settings (key, value) VALUES ('last_simulation_temperature', ?)", (str(params.temperature),))
            scur.execute("INSERT OR REPLACE INTO settings (key, value) VALUES ('last_simulation_humidity', ?)", (str(params.humidity),))
            scur.execute("INSERT OR REPLACE INTO settings (key, value) VALUES ('last_simulation_solar', ?)", (str(params.solar_intensity),))
            scur.execute("INSERT OR REPLACE INTO settings (key, value) VALUES ('last_simulation_wind', ?)", (str(params.wind_speed),))
            sconn.commit()
            sconn.close()
        except Exception as e:
            print(f"Error storing simulation parameters: {e}")
            pass
        # Backfill zone metrics from recent grid data
        try:
            backfill_zone_metrics_for_recent(50)
        except Exception:
            pass

        # Import CSV results if present and non-empty
        if os.path.exists(csv_path):
            try:
                # If file is empty, skip reading and consider synthetic generator results
                if os.path.getsize(csv_path) == 0:
                    return {"status": "Simulation completed (no CSV produced; synthetic generation applied)"}

                try:
                    df = pd.read_csv(csv_path)
                except pd.errors.EmptyDataError:
                    return {"status": "Simulation completed (CSV empty; synthetic generation applied)"}

                # If dataframe has no columns, skip gracefully
                if df is None or df.shape[1] == 0:
                    return {"status": "Simulation completed (CSV had no columns; synthetic generation applied)"}

                # Normalize columns
                col_map = {
                    'voltage': 'total_voltage',
                    'total_voltage': 'total_voltage',
                    'load': 'total_load',
                    'total_load': 'total_load',
                }
                rename = {}
                for c in df.columns:
                    k = str(c).strip()
                    if k in col_map:
                        rename[c] = col_map[k]
                df = df.rename(columns=rename)

                # Required columns
                for req in ['total_voltage', 'total_load']:
                    if req not in df.columns:
                        # If CSV doesn't contain required simulation columns, skip import
                        return {"status": "Simulation completed (CSV did not contain required columns; synthetic generation applied)"}

                # house_count removed; system uses zones
                if 'tick' not in df.columns:
                    # create sequential ticks
                    conn_tmp = sqlite3.connect(get_database_path())
                    cur = conn_tmp.cursor()
                    cur.execute('SELECT COALESCE(MAX(tick), 0) FROM grid_data')
                    start = cur.fetchone()[0] + 1
                    conn_tmp.close()
                    df['tick'] = range(start, start + len(df))

                conn = sqlite3.connect(get_database_path())
                df[['tick', 'total_voltage', 'total_load']].to_sql('grid_data', conn, if_exists='append', index=False)
                conn.close()
            except Exception as ie:
                raise HTTPException(status_code=500, detail=f'Failed to import simulation CSV: {ie}')

        return {"status": "Simulation completed"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/forecast")
def get_forecast(steps: int = 12):
    """
    Enhanced forecast endpoint with environmental factors.
    - Uses SARIMAX with environmental parameters when available
    - SVR prediction with environmental factor consideration
    - Returns both predictions and extended forecasts
    """
    try:
        models_path = get_models_path()
        
        # Load models with error handling
        svr = None
        scaler = None
        try:
            svr = joblib.load(os.path.join(models_path, 'svr_model.pkl'))
            scaler = joblib.load(os.path.join(models_path, 'scaler.pkl'))
        except Exception:
            pass

        # Get latest data with environmental parameters
        conn = sqlite3.connect(get_database_path())
        latest_df = pd.read_sql_query("""
            SELECT * FROM grid_data 
            ORDER BY tick DESC LIMIT 1
        """, conn)

        # Get recent history for modeling
        hist_df = pd.read_sql_query("""
            SELECT tick, total_load, total_voltage, temperature, humidity, 
                   solar_intensity, wind_speed, peak_hours, created_at
            FROM grid_data 
            ORDER BY tick DESC LIMIT 200
        """, conn)
        conn.close()

        if latest_df.empty:
            raise HTTPException(status_code=400, detail="No grid data available")

        # Environmental features
        env_cols = ['temperature', 'humidity', 'solar_intensity', 'wind_speed', 'peak_hours']
        available_env_cols = [col for col in env_cols if col in latest_df.columns and col in hist_df.columns]
        
        # Get current environmental conditions
        current_env = {}
        if available_env_cols:
            current_env = latest_df[available_env_cols].iloc[0].to_dict()

        # Load SARIMAX forecaster
        sarimax = None
        try:
            import sys
            import os
            current_dir = os.path.dirname(os.path.abspath(__file__))
            backend_dir = os.path.dirname(os.path.dirname(current_dir))
            project_dir = os.path.dirname(backend_dir)
            ml_models_dir = os.path.join(project_dir, 'ml_models')
            sys.path.insert(0, ml_models_dir)
            from sarimax_forecaster import SARIMAXForecaster
            sarimax = SARIMAXForecaster()
        except Exception as e:
            print(f"SARIMAX not available: {e}")

        # SVR prediction with environmental adjustment
        svr_pred = 800.0  # Default fallback
        if svr is not None and scaler is not None:
            try:
                X_cols = ['total_voltage']
                if 'house_count' in latest_df.columns:
                    X_cols.append('house_count')
                X = latest_df[X_cols]
                
                # Ensure feature compatibility
                n_features = getattr(scaler, 'n_features_in_', X.shape[1])
                if X.shape[1] != n_features:
                    if X.shape[1] < n_features:
                        import numpy as _np
                        pad = _np.zeros((X.shape[0], n_features - X.shape[1]))
                        X = _np.hstack([X.values, pad])
                    else:
                        X = X.iloc[:, :n_features].values
                
                X_scaled = scaler.transform(X)
                svr_pred = float(svr.predict(X_scaled)[0])
            except Exception:
                svr_pred = float(latest_df['total_load'].iloc[0]) if 'total_load' in latest_df.columns else 800.0

        # Apply environmental factors to SVR prediction
        if available_env_cols and current_env:
            temp_impact = (current_env.get('temperature', 25) - 25) * 3  # 3 kW per degree
            solar_impact = (current_env.get('solar_intensity', 50) - 50) * -1.5  # Solar reduces load
            wind_impact = current_env.get('wind_speed', 5) * -2  # Wind power reduces load
            peak_impact = current_env.get('peak_hours', 0) * 75  # 75 kW during peak hours
            humidity_impact = (current_env.get('humidity', 50) - 50) * 0.5  # Minor humidity effect
            
            env_adjustment = temp_impact + solar_impact + wind_impact + peak_impact + humidity_impact
            svr_pred += env_adjustment

        # SARIMAX prediction with environmental features
        sarimax_pred = None
        arima_next = svr_pred
        confidence = 0.7
        
        try:
            if sarimax and hasattr(sarimax, 'model') and sarimax.model is not None:
                if available_env_cols:
                    # Use latest environmental conditions for forecast
                    latest_env_df = latest_df[available_env_cols]
                    result = sarimax.forecast(steps=1, exog_future=latest_env_df)
                else:
                    result = sarimax.forecast(steps=1)
                
                if result and 'forecast' in result and result['forecast']:
                    sarimax_pred = float(result['forecast'][0])
                    arima_next = sarimax_pred
                    confidence = 0.85  # Higher confidence with environmental factors
        except Exception as e:
            print(f"SARIMAX forecast error: {e}")

        # Fallback ARIMA if SARIMAX unavailable
        arima_horizon = []
        if sarimax_pred is None:
            try:
                series = hist_df.iloc[::-1]['total_load'].astype(float).reset_index(drop=True)
                if len(series) >= 10 and STATSMODELS_AVAILABLE:
                    best_aic = float('inf')
                    best_model = None
                    for order in [(1,1,1), (2,1,1), (1,1,0)]:
                        try:
                            m = ARIMA(series, order=order)
                            fitted = m.fit()
                            if fitted.aic < best_aic:
                                best_aic = fitted.aic
                                best_model = fitted
                        except Exception:
                            continue
                    
                    if best_model is not None:
                        fcst_obj = best_model.get_forecast(steps=steps)
                        arima_vals = fcst_obj.predicted_mean.tolist()
                        arima_horizon = arima_vals
                        arima_next = float(arima_vals[0])
                        
                        # Adjust confidence based on environmental data availability
                        conf_int = fcst_obj.conf_int()
                        mean_level = max(1.0, float(series.iloc[-1]))
                        width = float(conf_int.iloc[0, 1] - conf_int.iloc[0, 0])
                        rel_width = min(1.0, max(0.0, width / mean_level))
                        base_confidence = max(0.1, 1.0 - rel_width)
                        confidence = base_confidence + (0.1 if available_env_cols else 0)
                else:
                    # Simple moving average fallback
                    window = min(10, len(series)) if len(series) > 0 else 0
                    if window > 0:
                        arima_next = float(series.tail(window).mean())
                        arima_horizon = [arima_next for _ in range(steps)]
                        confidence = 0.5
            except Exception:
                arima_next = svr_pred
                arima_horizon = [svr_pred for _ in range(steps)]

        # Generate extended horizon if SARIMAX available
        if sarimax_pred is not None and sarimax:
            try:
                if available_env_cols:
                    # Replicate environmental conditions for extended forecast
                    env_future = pd.concat([latest_df[available_env_cols]] * steps, ignore_index=True)
                    extended_result = sarimax.forecast(steps=steps, exog_future=env_future)
                else:
                    extended_result = sarimax.forecast(steps=steps)
                
                if extended_result and 'forecast' in extended_result:
                    arima_horizon = [float(x) for x in extended_result['forecast']]
            except Exception:
                pass

        # Ensemble prediction with environmental weighting
        env_weight = 0.15 if available_env_cols else 0
        base_weight = 0.5
        ensemble_pred = (base_weight - env_weight) * svr_pred + (base_weight + env_weight) * arima_next

        # Generate extended forecasts for multiple horizons
        extended_forecasts = {}
        if sarimax:
            horizons = {
                'hourly': 60,      # 1 hour (60 minutes)
                'daily': 1440,     # 1 day (1440 minutes)
                'weekly': 10080,   # 1 week
                'monthly': 43200   # 1 month (30 days)
            }
            
            for horizon_name, horizon_steps in horizons.items():
                try:
                    if available_env_cols:
                        # Create realistic environmental projections
                        env_future = []
                        for i in range(horizon_steps):
                            env_row = current_env.copy()
                            # Add realistic variations
                            if 'temperature' in env_row:
                                env_row['temperature'] += np.random.normal(0, 2)
                            if 'humidity' in env_row:
                                env_row['humidity'] = max(0, min(100, env_row['humidity'] + np.random.normal(0, 5)))
                            if 'solar_intensity' in env_row:
                                env_row['solar_intensity'] = max(0, min(100, env_row['solar_intensity'] + np.random.normal(0, 10)))
                            if 'wind_speed' in env_row:
                                env_row['wind_speed'] = max(0, env_row['wind_speed'] + np.random.normal(0, 2))
                            if 'peak_hours' in env_row:
                                # Simple daily cycle for peak hours
                                hour_in_day = (i // 60) % 24
                                env_row['peak_hours'] = 1 if 9 <= hour_in_day <= 18 else 0
                            env_future.append(env_row)
                        
                        env_future_df = pd.DataFrame(env_future)
                        horizon_result = sarimax.forecast(steps=horizon_steps, exog_future=env_future_df)
                    else:
                        horizon_result = sarimax.forecast(steps=horizon_steps)
                    
                    if horizon_result and 'forecast' in horizon_result:
                        # Sample the forecast (take every nth point for performance)
                        sample_interval = max(1, horizon_steps // 50)  # Max 50 points per horizon
                        sampled_forecast = horizon_result['forecast'][::sample_interval]
                        extended_forecasts[horizon_name] = [float(x) for x in sampled_forecast]
                except Exception as e:
                    print(f"Extended forecast error for {horizon_name}: {e}")

        return {
            "svr_prediction": float(svr_pred),
            "arima_prediction": float(arima_next),
            "sarimax_prediction": float(sarimax_pred) if sarimax_pred else None,
            "ensemble_prediction": float(ensemble_pred),
            "confidence": float(confidence),
            "arima_forecast": arima_horizon,
            "environmental_factors": current_env,
            "uses_environmental_data": bool(available_env_cols),
            "extended_forecasts": extended_forecasts,
            "forecast_period": f"next_{steps}_steps",
            "timestamp": datetime.datetime.now().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Forecasting error: {str(e)}")

@router.get("/voltage-forecast")
def get_voltage_forecast():
    """Get enhanced SARIMAX-based voltage forecasting with environmental parameters"""
    try:
        # Get historical voltage data
        conn = sqlite3.connect(get_database_path())
        
        # Get last 100 records for better forecasting accuracy
        df = pd.read_sql_query("""
            SELECT tick, total_voltage, temperature, humidity, 
                   solar_intensity, wind_speed, peak_hours, created_at
            FROM grid_data 
            ORDER BY tick DESC LIMIT 100
        """, conn)
        conn.close()
        
        if df.empty or len(df) < 10:
            # Generate simulation-based forecast when no historical data
            return generate_simulation_voltage_forecast()
        
        # Reverse to get chronological order
        df = df.iloc[::-1].reset_index(drop=True)
        
        # Fix unrealistic voltage values by scaling them to proper range (220-240V)
        raw_voltage = df['total_voltage']
        if raw_voltage.mean() > 1000:  # If values are unrealistically high
            # Scale down to realistic voltage range
            voltage_series = (raw_voltage / 100).clip(200, 250)
        else:
            voltage_series = raw_voltage.clip(200, 250)
        
        # Update the dataframe with realistic voltage
        df['total_voltage'] = voltage_series
        
        # Environmental features for enhanced forecasting
        exog_cols = ['temperature', 'humidity', 'solar_intensity', 'wind_speed', 'peak_hours']
        available_exog_cols = [col for col in exog_cols if col in df.columns and not df[col].isna().all()]
        
        # Get current environmental parameters
        current_env = {}
        if available_exog_cols:
            # Fill NaN values with reasonable defaults
            df['temperature'] = df['temperature'].fillna(25.0)
            df['humidity'] = df['humidity'].fillna(60.0) 
            df['solar_intensity'] = df['solar_intensity'].fillna(500.0)
            df['wind_speed'] = df['wind_speed'].fillna(10.0)
            df['peak_hours'] = df['peak_hours'].fillna(0)
            current_env = df[available_exog_cols].iloc[-1].to_dict()
        
        # Enhanced SARIMAX forecasting with environmental factors
        if not STATSMODELS_AVAILABLE:
            return {
                "error": "SARIMAX forecasting requires statsmodels package",
                "hourly_forecast": [],
                "daily_forecast": []
            }
        
        # Use SARIMAX for better environmental integration
        try:
            if available_exog_cols:
                exog_data = df[available_exog_cols].values
                from statsmodels.tsa.statespace.sarimax import SARIMAX
                model = SARIMAX(voltage_series, exog=exog_data, order=(1, 1, 1))
                best_model = model.fit(disp=False)
            else:
                # Fallback to ARIMA if no environmental data
                model = ARIMA(voltage_series, order=(1, 1, 1))
                best_model = model.fit()
        except Exception as e:
            # Fallback to simple ARIMA
            model = ARIMA(voltage_series, order=(1, 1, 1))
            best_model = model.fit()
            available_exog_cols = []
        
        # Generate forecasts with enhanced environmental response
        steps_1_hour = 60  # 60 minutes
        steps_1_day = 1440  # 1440 minutes = 24 hours
        
        # Create future environmental data with realistic variations
        future_exog_1h = None
        future_exog_1d = None
        
        if available_exog_cols and hasattr(best_model.model, 'k_exog') and best_model.model.k_exog > 0:
            # Generate future environmental parameters with realistic variations
            base_temp = current_env.get('temperature', 25.0)
            base_humidity = current_env.get('humidity', 60.0)
            base_solar = current_env.get('solar_intensity', 500.0)
            base_wind = current_env.get('wind_speed', 10.0)
            base_peak = current_env.get('peak_hours', 0)
            
            # Hourly future environmental data
            future_env_1h = []
            for i in range(steps_1_hour):
                # Add realistic hourly variations
                hour_factor = i / 60.0  # Hour progression
                temp_var = base_temp + 3.0 * np.sin(2 * np.pi * hour_factor) + np.random.normal(0, 1)
                humidity_var = base_humidity + 10.0 * np.cos(2 * np.pi * hour_factor) + np.random.normal(0, 5)
                solar_var = max(0, base_solar * (0.5 + 0.5 * np.sin(2 * np.pi * hour_factor)) + np.random.normal(0, 50))
                wind_var = max(0, base_wind + 5.0 * np.sin(2 * np.pi * hour_factor / 2) + np.random.normal(0, 2))
                peak_var = 1 if 8 <= (hour_factor * 24) % 24 <= 20 else 0  # Peak hours 8AM-8PM
                
                future_env_1h.append([temp_var, humidity_var, solar_var, wind_var, peak_var])
            
            future_exog_1h = np.array(future_env_1h)
            
            # Daily future environmental data
            future_env_1d = []
            for i in range(steps_1_day):
                hour_factor = i / 60.0  # Hour progression
                day_factor = i / 1440.0  # Day progression
                temp_var = base_temp + 5.0 * np.sin(2 * np.pi * hour_factor) + 2.0 * np.sin(2 * np.pi * day_factor) + np.random.normal(0, 1)
                humidity_var = base_humidity + 15.0 * np.cos(2 * np.pi * hour_factor) + np.random.normal(0, 5)
                solar_var = max(0, base_solar * (0.3 + 0.7 * np.sin(2 * np.pi * hour_factor)) + np.random.normal(0, 100))
                wind_var = max(0, base_wind + 8.0 * np.sin(2 * np.pi * hour_factor / 3) + np.random.normal(0, 3))
                peak_var = 1 if 8 <= (hour_factor * 24) % 24 <= 20 else 0
                
                future_env_1d.append([temp_var, humidity_var, solar_var, wind_var, peak_var])
            
            future_exog_1d = np.array(future_env_1d)
        
        # Forecast for 1 hour
        if future_exog_1h is not None:
            hourly_forecast = best_model.get_forecast(steps=steps_1_hour, exog=future_exog_1h)
            hourly_mean = hourly_forecast.predicted_mean
            hourly_conf_int = hourly_forecast.conf_int()
        else:
            hourly_forecast = best_model.forecast(steps=steps_1_hour)
            hourly_mean = hourly_forecast
            hourly_conf_int = best_model.get_forecast(steps=steps_1_hour).conf_int()
        
        # Forecast for 1 day
        if future_exog_1d is not None:
            daily_forecast = best_model.get_forecast(steps=steps_1_day, exog=future_exog_1d)
            daily_mean = daily_forecast.predicted_mean
            daily_conf_int = daily_forecast.conf_int()
        else:
            daily_forecast = best_model.forecast(steps=steps_1_day)
            daily_mean = daily_forecast
            daily_conf_int = best_model.get_forecast(steps=steps_1_day).conf_int()
        
        # Get current time for forecast timestamps
        import datetime
        current_time = datetime.datetime.now()
        
        # Prepare hourly forecast data
        hourly_data = []
        for i in range(steps_1_hour):
            forecast_time = current_time + datetime.timedelta(minutes=i+1)
            voltage_val = float(hourly_mean.iloc[i]) if hasattr(hourly_mean, 'iloc') else float(hourly_mean[i])
            lower_val = float(hourly_conf_int.iloc[i, 0]) if hasattr(hourly_conf_int, 'iloc') else voltage_val - 5
            upper_val = float(hourly_conf_int.iloc[i, 1]) if hasattr(hourly_conf_int, 'iloc') else voltage_val + 5
            
            hourly_data.append({
                "time": forecast_time.isoformat(),
                "voltage": voltage_val,
                "confidence_lower": lower_val,
                "confidence_upper": upper_val
            })
        
        # Prepare daily forecast data (sample every 60 minutes for readability)
        daily_data = []
        for i in range(0, steps_1_day, 60):  # Sample every hour
            forecast_time = current_time + datetime.timedelta(minutes=i+1)
            voltage_val = float(daily_mean.iloc[i]) if hasattr(daily_mean, 'iloc') else float(daily_mean[i])
            lower_val = float(daily_conf_int.iloc[i, 0]) if hasattr(daily_conf_int, 'iloc') else voltage_val - 5
            upper_val = float(daily_conf_int.iloc[i, 1]) if hasattr(daily_conf_int, 'iloc') else voltage_val + 5
            
            daily_data.append({
                "time": forecast_time.isoformat(),
                "voltage": voltage_val,
                "confidence_lower": lower_val,
                "confidence_upper": upper_val
            })
        
        # Calculate forecast statistics
        current_voltage = float(voltage_series.iloc[-1])
        hourly_avg = float(hourly_mean.mean()) if hasattr(hourly_mean, 'mean') else float(np.mean(hourly_mean))
        daily_avg = float(daily_mean.mean()) if hasattr(daily_mean, 'mean') else float(np.mean(daily_mean))
        
        # Enhanced voltage trend analysis with environmental factors
        hourly_trend = "stable"
        daily_trend = "stable"
        
        # Consider both statistical and environmental trends
        voltage_change_1h = (hourly_avg - current_voltage) / current_voltage * 100
        voltage_change_1d = (daily_avg - current_voltage) / current_voltage * 100
        
        if voltage_change_1h > 2:
            hourly_trend = "increasing"
        elif voltage_change_1h < -2:
            hourly_trend = "decreasing"
            
        if voltage_change_1d > 3:
            daily_trend = "increasing"
        elif voltage_change_1d < -3:
            daily_trend = "decreasing"
        
        # Environmental impact assessment
        env_impact = {}
        if current_env:
            temp = current_env.get('temperature', 25)
            solar = current_env.get('solar_intensity', 500)
            wind = current_env.get('wind_speed', 10)
            
            env_impact = {
                "temperature_effect": "heating_load" if temp > 30 else "cooling_load" if temp < 15 else "normal",
                "solar_contribution": "high" if solar > 700 else "medium" if solar > 300 else "low",
                "wind_contribution": "high" if wind > 15 else "medium" if wind > 5 else "low"
            }
        
        return {
            "current_voltage": current_voltage,
            "forecast_timestamp": current_time.isoformat(),
            "model_info": {
                "aic": float(best_model.aic),
                "model_type": "SARIMAX" if available_exog_cols else "ARIMA",
                "environmental_factors": len(available_exog_cols),
                "order": getattr(best_model.specification, 'order', (1,1,1))
            },
            "environmental_impact": env_impact,
            "hourly_forecast": {
                "data": hourly_data,
                "average": hourly_avg,
                "trend": hourly_trend,
                "change_percent": round(voltage_change_1h, 2),
                "min_voltage": float(hourly_mean.min()) if hasattr(hourly_mean, 'min') else float(min(hourly_mean)),
                "max_voltage": float(hourly_mean.max()) if hasattr(hourly_mean, 'max') else float(max(hourly_mean))
            },
            "daily_forecast": {
                "data": daily_data,
                "average": daily_avg,
                "trend": daily_trend,
                "change_percent": round(voltage_change_1d, 2),
                "min_voltage": float(daily_mean.min()) if hasattr(daily_mean, 'min') else float(min(daily_mean)),
                "max_voltage": float(daily_mean.max()) if hasattr(daily_mean, 'max') else float(max(daily_mean))
            },
            "current_conditions": current_env
        }
    
    except Exception as e:
        return {
            "error": f"Voltage forecasting error: {str(e)}",
            "hourly_forecast": [],
            "daily_forecast": []
        }


def generate_simulation_voltage_forecast():
    """Generate voltage forecast based on current simulation parameters when no historical data exists."""
    try:
        import datetime
        current_time = datetime.datetime.now()
        
        # Try to get current simulation values from multiple sources
        simulation_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'simulation')
        grid_file = os.path.join(simulation_dir, 'grid_data.csv')
        
        base_voltage = 220.0
        base_temp = 25.0
        base_solar = 500.0
        base_wind = 10.0
        base_humidity = 60.0
        
        # Try to get latest simulation data from database first (most recent)
        try:
            conn = sqlite3.connect(os.path.join(os.path.dirname(__file__), '..', '..', 'database.db'))
            result = conn.execute("""
                SELECT total_voltage, temperature, humidity, solar_intensity, wind_speed 
                FROM grid_data 
                ORDER BY tick DESC LIMIT 1
            """).fetchone()
            conn.close()
            
            if result:
                raw_voltage, temp, humidity, solar, wind = result
                # Scale voltage to realistic range if needed
                base_voltage = (raw_voltage / 100) if raw_voltage > 1000 else raw_voltage
                base_voltage = max(200, min(250, base_voltage))
                base_temp = temp if temp is not None else 25.0
                base_humidity = humidity if humidity is not None else 60.0
                base_solar = solar if solar is not None else 500.0
                base_wind = wind if wind is not None else 10.0
        except:
            pass
        
        # Try CSV file as backup
        if os.path.exists(grid_file):
            try:
                df = pd.read_csv(grid_file)
                if not df.empty:
                    latest = df.iloc[-1]
                    if 'total_voltage' in latest:
                        raw_voltage = latest['total_voltage']
                        # Scale voltage to realistic range if needed
                        base_voltage = (raw_voltage / 100) if raw_voltage > 1000 else raw_voltage
                        base_voltage = max(200, min(250, base_voltage))
                    if 'temperature' in latest:
                        base_temp = latest['temperature']
                    if 'humidity' in latest:
                        base_humidity = latest['humidity']
                    if 'solar_intensity' in latest:
                        base_solar = latest['solar_intensity']
                    if 'wind_speed' in latest:
                        base_wind = latest['wind_speed']
            except:
                pass
        
        # Generate responsive forecast
        steps_1_hour = 60
        steps_1_day = 1440
        
        # Hourly forecast
        hourly_data = []
        for i in range(steps_1_hour):
            forecast_time = current_time + datetime.timedelta(minutes=i+1)
            
            # Environmental effects
            hour_progress = i / 60.0
            temp_effect = (base_temp - 25) * 0.5  # Temperature impact
            solar_effect = base_solar / 1000.0 * 3.0 * np.sin(2 * np.pi * hour_progress)  # Solar cycles
            wind_effect = base_wind / 20.0 * 2.0 * np.cos(2 * np.pi * hour_progress / 2)  # Wind patterns
            
            # Voltage prediction with environmental responsiveness
            voltage = base_voltage + temp_effect + solar_effect + wind_effect + np.random.normal(0, 1.5)
            voltage = max(200, min(250, voltage))
            
            hourly_data.append({
                "time": forecast_time.isoformat(),
                "voltage": round(voltage, 2),
                "confidence_lower": round(voltage - 5, 2),
                "confidence_upper": round(voltage + 5, 2)
            })
        
        # Daily forecast (sample every hour)
        daily_data = []
        for i in range(0, steps_1_day, 60):
            forecast_time = current_time + datetime.timedelta(minutes=i+1)
            
            hour_in_day = (i / 60.0) % 24
            day_progress = i / 1440.0
            
            # Daily patterns
            temp_daily = (base_temp - 25) * 0.5
            solar_daily = base_solar / 1000.0 * 4.0 * np.sin(2 * np.pi * hour_in_day / 24)
            wind_daily = base_wind / 20.0 * 3.0 * np.cos(2 * np.pi * hour_in_day / 12)
            
            voltage = base_voltage + temp_daily + solar_daily + wind_daily + np.random.normal(0, 2)
            voltage = max(200, min(250, voltage))
            
            daily_data.append({
                "time": forecast_time.isoformat(),
                "voltage": round(voltage, 2),
                "confidence_lower": round(voltage - 7, 2),
                "confidence_upper": round(voltage + 7, 2)
            })
        
        # Calculate averages and trends
        hourly_voltages = [d["voltage"] for d in hourly_data]
        daily_voltages = [d["voltage"] for d in daily_data]
        
        hourly_avg = np.mean(hourly_voltages)
        daily_avg = np.mean(daily_voltages)
        
        hourly_trend = "increasing" if hourly_avg > base_voltage * 1.02 else "decreasing" if hourly_avg < base_voltage * 0.98 else "stable"
        daily_trend = "increasing" if daily_avg > base_voltage * 1.03 else "decreasing" if daily_avg < base_voltage * 0.97 else "stable"
        
        return {
            "current_voltage": base_voltage,
            "forecast_timestamp": current_time.isoformat(),
            "model_info": {
                "aic": 100.0,
                "model_type": "Simulation-based",
                "environmental_factors": 3,
                "order": (1, 1, 1)
            },
            "environmental_impact": {
                "temperature_effect": "heating_load" if base_temp > 30 else "cooling_load" if base_temp < 15 else "normal",
                "solar_contribution": "high" if base_solar > 700 else "medium" if base_solar > 300 else "low",
                "wind_contribution": "high" if base_wind > 15 else "medium" if base_wind > 5 else "low"
            },
            "hourly_forecast": {
                "data": hourly_data,
                "average": round(hourly_avg, 2),
                "trend": hourly_trend,
                "change_percent": round((hourly_avg - base_voltage) / base_voltage * 100, 2),
                "min_voltage": round(min(hourly_voltages), 2),
                "max_voltage": round(max(hourly_voltages), 2)
            },
            "daily_forecast": {
                "data": daily_data,
                "average": round(daily_avg, 2),
                "trend": daily_trend,
                "change_percent": round((daily_avg - base_voltage) / base_voltage * 100, 2),
                "min_voltage": round(min(daily_voltages), 2),
                "max_voltage": round(max(daily_voltages), 2)
            },
            "current_conditions": {
                "temperature": base_temp,
                "solar_intensity": base_solar,
                "wind_speed": base_wind,
                "humidity": 60.0,
                "peak_hours": 1 if 8 <= current_time.hour <= 20 else 0
            }
        }
    
    except Exception as e:
        return {
            "error": f"Simulation forecast error: {str(e)}",
            "hourly_forecast": [],
            "daily_forecast": []
        }


@router.get("/forecast-summary")
def get_forecast_summary():
    """Get a summary of voltage forecasting with key insights"""
    try:
        voltage_forecast = get_voltage_forecast()
        
        if "error" in voltage_forecast:
            return voltage_forecast
        
        # Extract key insights
        current_voltage = voltage_forecast["current_voltage"]
        hourly_avg = voltage_forecast["hourly_forecast"]["average"]
        daily_avg = voltage_forecast["daily_forecast"]["average"]
        
        # Calculate percentage changes
        hourly_change = ((hourly_avg - current_voltage) / current_voltage) * 100
        daily_change = ((daily_avg - current_voltage) / current_voltage) * 100
        
        # Generate alerts based on forecast
        alerts = []
        
        if hourly_avg < 20000:
            alerts.append({
                "type": "warning",
                "message": "Voltage expected to drop below 20kV in the next hour",
                "severity": "medium"
            })
        
        if daily_avg < 18000:
            alerts.append({
                "type": "critical",
                "message": "Voltage expected to drop below 18kV in the next 24 hours",
                "severity": "high"
            })
        
        if abs(hourly_change) > 10:
            alerts.append({
                "type": "info",
                "message": f"Significant voltage change expected: {hourly_change:.1f}% in next hour",
                "severity": "low"
            })
        
        return {
            "current_voltage": current_voltage,
            "forecast_timestamp": voltage_forecast["forecast_timestamp"],
            "predictions": {
                "next_hour": {
                    "average_voltage": hourly_avg,
                    "change_percentage": hourly_change,
                    "trend": voltage_forecast["hourly_forecast"]["trend"]
                },
                "next_day": {
                    "average_voltage": daily_avg,
                    "change_percentage": daily_change,
                    "trend": voltage_forecast["daily_forecast"]["trend"]
                }
            },
            "alerts": alerts,
            "confidence": "high" if voltage_forecast["model_info"]["aic"] < 1000 else "medium"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating forecast summary: {str(e)}")


@router.post("/upload-excel")
async def upload_excel_file(file: UploadFile = File(...)):
    """Upload and process Excel file (voltage & load). Zones are managed via the zones API."""
    try:
        if not file.filename.endswith(('.xlsx', '.xls')):
            raise HTTPException(status_code=400, detail="Invalid file type. Please upload an Excel file.")

        contents = await file.read()
        try:
            df = pd.read_excel(io.BytesIO(contents))
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to read Excel file: {str(e)}")

        # Require basic columns
        required = ['voltage', 'load']
        missing = [c for c in required if c not in df.columns]
        if missing:
            raise HTTPException(status_code=400, detail=f"Missing required columns: {', '.join(missing)}")

        rows = []
        for _, r in df.iterrows():
            rows.append({'tick': None, 'total_voltage': r.get('voltage', 0), 'total_load': r.get('load', 0), 'timestamp': datetime.datetime.now().isoformat()})

        conn = sqlite3.connect(get_database_path())
        cur = conn.cursor()
        cur.execute('SELECT COALESCE(MAX(tick), 0) FROM grid_data')
        start = cur.fetchone()[0] + 1
        for i, row in enumerate(rows):
            row['tick'] = start + i
        if rows:
            pd.DataFrame(rows).to_sql('grid_data', conn, if_exists='append', index=False)
        conn.close()
        return {"message": "File uploaded and processed successfully", "rows_processed": len(rows), "filename": file.filename}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")


@router.get("/export-data")
async def export_data():
    """Export all system data as CSV"""
    try:
        conn = sqlite3.connect(get_database_path())
        grid_data = pd.read_sql_query("SELECT * FROM grid_data ORDER BY tick", conn)
        summary_stats = pd.read_sql_query("""
            SELECT
                COUNT(*) as total_records,
                AVG(total_voltage) as avg_voltage,
                AVG(total_load) as avg_load,
                MIN(total_voltage) as min_voltage,
                MAX(total_voltage) as max_voltage,
                MIN(total_load) as min_load,
                MAX(total_load) as max_load
            FROM grid_data
        """, conn)
        conn.close()

        output = io.StringIO()
        output.write("POWER GRID SYSTEM SUMMARY\n")
        output.write("=" * 50 + "\n")
        output.write(f"Export Date: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        output.write(f"Total Records: {summary_stats['total_records'].iloc[0]}\n")
        output.write(f"Average Voltage: {summary_stats['avg_voltage'].iloc[0]:.2f}V\n")
        output.write(f"Average Load: {summary_stats['avg_load'].iloc[0]:.2f}kW\n")
        output.write(f"Voltage Range: {summary_stats['min_voltage'].iloc[0]:.2f}V - {summary_stats['max_voltage'].iloc[0]:.2f}V\n")
        output.write(f"Load Range: {summary_stats['min_load'].iloc[0]:.2f}kW - {summary_stats['max_load'].iloc[0]:.2f}kW\n")
        output.write("\n")
        output.write("DETAILED GRID DATA\n")
        output.write("=" * 50 + "\n")
        grid_data.to_csv(output, index=False)
        csv_content = output.getvalue()
        output.close()
        return StreamingResponse(io.BytesIO(csv_content.encode('utf-8')), media_type='text/csv', headers={
            'Content-Disposition': f'attachment; filename="power_grid_export_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.csv"'
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error exporting data: {str(e)}")


@router.get("/data-statistics")
async def get_data_statistics():
    """Get statistics about the stored data"""
    try:
        conn = sqlite3.connect(get_database_path())
        stats = pd.read_sql_query("""
            SELECT 
                COUNT(*) as total_records,
                MIN(created_at) as oldest_record,
                MAX(created_at) as newest_record,
                AVG(total_voltage) as avg_voltage,
                AVG(total_load) as avg_load
            FROM grid_data
        """, conn)
        conn.close()
        if stats.empty or stats['total_records'].iloc[0] == 0:
            return {"total_records": 0, "oldest_record": None, "newest_record": None, "avg_voltage": 0, "avg_load": 0, "estimated_size": "0 KB"}
        estimated_size_kb = stats['total_records'].iloc[0] * 0.1
        size_unit = "KB"
        if estimated_size_kb > 1024:
            estimated_size_kb = estimated_size_kb / 1024
            size_unit = "MB"
        return {"total_records": int(stats['total_records'].iloc[0]), "oldest_record": stats['oldest_record'].iloc[0], "newest_record": stats['newest_record'].iloc[0], "avg_voltage": float(stats['avg_voltage'].iloc[0]), "avg_load": float(stats['avg_load'].iloc[0]), "estimated_size": f"{estimated_size_kb:.1f} {size_unit}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting statistics: {str(e)}")

@router.post("/generator/toggle")
def toggle_generator():
    """Toggle the backup generator on/off"""
    try:
        conn = sqlite3.connect(get_database_path())
        cursor = conn.cursor()
        
        # Create settings table if it doesn't exist
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Get current generator status
        cursor.execute("SELECT value FROM settings WHERE key='generator_enabled'")
        current = cursor.fetchone()
        current_status = bool(current and str(current[0]) == '1') if current else False
        
        # Toggle the status
        new_status = not current_status
        new_value = '1' if new_status else '0'
        
        # Update the setting
        cursor.execute("""
            INSERT OR REPLACE INTO settings (key, value, updated_at) 
            VALUES (?, ?, CURRENT_TIMESTAMP)
        """, ('generator_enabled', new_value))
        
        conn.commit()
        conn.close()
        
        return {
            "success": True,
            "generator_enabled": new_status,
            "message": f"Generator {'enabled' if new_status else 'disabled'} successfully",
            "timestamp": pd.Timestamp.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error toggling generator: {str(e)}")

@router.get("/generator/status")
def get_generator_status():
    """Get current generator status"""
    try:
        conn = sqlite3.connect(get_database_path())
        cursor = conn.cursor()
        cursor.execute("SELECT value FROM settings WHERE key='generator_enabled'")
        result = cursor.fetchone()
        conn.close()
        
        enabled = bool(result and str(result[0]) == '1') if result else False
        
        return {
            "generator_enabled": enabled,
            "status": "online" if enabled else "offline",
            "timestamp": pd.Timestamp.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting generator status: {str(e)}")