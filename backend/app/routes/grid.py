from fastapi import APIRouter, HTTPException, UploadFile, File
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import pandas as pd
import sqlite3
import joblib
import subprocess
import os
import datetime
import warnings
import io
from ..utils.netlogo import run_netlogo_simulation, backfill_zone_metrics_for_recent
from ml_models.sarimax_forecaster import SARIMAXForecaster

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
    voltage: float = 22500

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
        return df.to_dict(orient='records')[0]
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
        status = "healthy"
        
        if avg_voltage < 20000 or avg_load > 1200:
            status = "warning"
        if avg_voltage < 15000 or avg_load > 1500:
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

        # Recommend action
        recommended_action = None
        if status in ("warning", "critical") and not generator_enabled:
            recommended_action = "enable_generator"

        return {
            "status": status,
            "total_records": int(total_count),
            "latest_tick": int(latest_df['tick'].iloc[0]),
            "averages": {
                "voltage": float(avg_df['avg_voltage'].iloc[0]),
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
    Combined forecast endpoint.
    - SVR uses the saved scaler and model on latest features.
    - ARIMA is fit on recent total_load values so it reflects new simulation data.
    Returns both single-step predictions and a short ARIMA horizon for charts.
    """
    try:
        models_path = get_models_path()
        svr = joblib.load(os.path.join(models_path, 'svr_model.pkl'))
        scaler = joblib.load(os.path.join(models_path, 'scaler.pkl'))

        # Latest row for SVR features
        conn = sqlite3.connect(get_database_path())
        latest_df = pd.read_sql_query("SELECT * FROM grid_data ORDER BY tick DESC LIMIT 1", conn)

        # Recent history for ARIMA (use load as target)
        hist_df = pd.read_sql_query(
            "SELECT total_load FROM grid_data ORDER BY tick DESC LIMIT 200",
            conn,
        )
        conn.close()

        if latest_df.empty:
            raise HTTPException(status_code=400, detail="No grid data available")

        # load models and prefer SARIMAX if available
        sarimax = SARIMAXForecaster()

        # SVR prediction: adapt to model feature size (may be 1 or 2 features).
        # Prefer ['total_voltage', 'house_count'] if present, otherwise use ['total_voltage'].
        X_cols = ['total_voltage']
        if 'house_count' in latest_df.columns:
            X_cols.append('house_count')
        X = latest_df[X_cols]
        # Ensure the feature count matches what the scaler/model expect. If needed pad with zeros or trim.
        try:
            n_features = getattr(scaler, 'n_features_in_', None)
            if n_features is None and hasattr(scaler, 'mean_'):
                n_features = len(scaler.mean_)
            if n_features is not None and X.shape[1] != n_features:
                # Pad with zeros if model expects more features
                if X.shape[1] < n_features:
                    import numpy as _np
                    pad = _np.zeros((X.shape[0], n_features - X.shape[1]))
                    X = _np.hstack([X.values, pad])
                else:
                    # Trim extra columns
                    X = X.iloc[:, :n_features].values
        except Exception:
            # Fallback: convert to numpy array
            X = X.values

        X_scaled = scaler.transform(X)
        svr_pred = float(svr.predict(X_scaled)[0])

        # SARIMAX forecast (if model exists)
        sarimax_pred = None
        try:
            sarimax_pred = sarimax.forecast(steps=steps)
        except Exception:
            sarimax_pred = None

        # ARIMA prediction using recent data; fallback to moving average if statsmodels unavailable
        arima_next = None
        arima_horizon = []
        confidence = 0.6  # base default

        try:
            series = hist_df.iloc[::-1]['total_load'].astype(float).reset_index(drop=True)
            if len(series) >= 10 and STATSMODELS_AVAILABLE:
                # Fit a lightweight ARIMA; choose among a few small orders
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
                if best_model is None:
                    best_model = ARIMA(series, order=(1,1,1)).fit()

                fcst_obj = best_model.get_forecast(steps=10)
                arima_vals = fcst_obj.predicted_mean.tolist()
                conf_int = fcst_obj.conf_int()
                arima_horizon = arima_vals
                arima_next = float(arima_vals[0])
                # Confidence inversely related to relative interval width
                mean_level = max(1.0, float(series.iloc[-1]))
                width = float(conf_int.iloc[0, 1] - conf_int.iloc[0, 0])
                rel_width = min(1.0, max(0.0, width / mean_level))
                confidence = float(max(0.1, 1.0 - rel_width))
            else:
                # Fallback: simple moving average of last N
                window = min(10, len(series)) if len(series) > 0 else 0
                if window > 0:
                    arima_next = float(series.tail(window).mean())
                    # Produce a flat short horizon
                    arima_horizon = [arima_next for _ in range(10)]
                    confidence = 0.4
        except Exception:
            # Keep defaults if anything goes wrong
            pass

        # If ARIMA couldn't be computed, align with SVR as a crude fallback
        if arima_next is None:
            arima_next = svr_pred
            arima_horizon = [svr_pred for _ in range(10)]

        # Simple ensemble: average of SVR and ARIMA
        ensemble_pred = float((svr_pred + arima_next) / 2.0)

        return {
            "svr_prediction": svr_pred,
            "arima_prediction": arima_next,
            "sarimax_prediction": sarimax_pred,
            "ensemble_prediction": ensemble_pred,
            "confidence": confidence,
            # keep backward compatibility with existing UI pieces
            "arima_forecast": arima_horizon,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/voltage-forecast")
def get_voltage_forecast():
    """Get ARIMA-based voltage forecasting for 1 hour and 1 day"""
    try:
        # Get historical voltage data
        conn = sqlite3.connect(get_database_path())
        
        # Get last 100 records for better forecasting accuracy
        df = pd.read_sql_query("SELECT tick, total_voltage FROM grid_data ORDER BY tick DESC LIMIT 100", conn)
        conn.close()
        
        if df.empty or len(df) < 10:
            return {
                "error": "Insufficient historical data for forecasting",
                "hourly_forecast": [],
                "daily_forecast": []
            }
        
        # Reverse to get chronological order
        df = df.iloc[::-1].reset_index(drop=True)
        voltage_series = df['total_voltage']
        
        # Fit ARIMA model specifically for voltage forecasting
        if not STATSMODELS_AVAILABLE:
            return {
                "error": "ARIMA forecasting requires statsmodels package",
                "hourly_forecast": [],
                "daily_forecast": []
            }
        
        # Try different ARIMA parameters to find the best fit
        best_aic = float('inf')
        best_model = None
        
        for p in range(0, 3):
            for d in range(0, 2):
                for q in range(0, 3):
                    try:
                        model = ARIMA(voltage_series, order=(p, d, q))
                        fitted = model.fit()
                        if fitted.aic < best_aic:
                            best_aic = fitted.aic
                            best_model = fitted
                    except:
                        continue
        
        if best_model is None:
            # Fallback to simple ARIMA(1,1,1)
            model = ARIMA(voltage_series, order=(1, 1, 1))
            best_model = model.fit()
        
        # Generate forecasts
        # Assuming 1 tick = 1 minute (adjust as needed)
        steps_1_hour = 60  # 60 minutes
        steps_1_day = 1440  # 1440 minutes = 24 hours
        
        # Forecast for 1 hour (60 steps)
        hourly_forecast = best_model.forecast(steps=steps_1_hour)
        hourly_conf_int = best_model.get_forecast(steps=steps_1_hour).conf_int()
        
        # Forecast for 1 day (1440 steps)
        daily_forecast = best_model.forecast(steps=steps_1_day)
        daily_conf_int = best_model.get_forecast(steps=steps_1_day).conf_int()
        
        # Get current time for forecast timestamps
        import datetime
        current_time = datetime.datetime.now()
        
        # Prepare hourly forecast data
        hourly_data = []
        for i in range(steps_1_hour):
            forecast_time = current_time + datetime.timedelta(minutes=i+1)
            hourly_data.append({
                "time": forecast_time.isoformat(),
                "voltage": float(hourly_forecast.iloc[i]),
                "confidence_lower": float(hourly_conf_int.iloc[i, 0]),
                "confidence_upper": float(hourly_conf_int.iloc[i, 1])
            })
        
        # Prepare daily forecast data (sample every 60 minutes for readability)
        daily_data = []
        for i in range(0, steps_1_day, 60):  # Sample every hour
            forecast_time = current_time + datetime.timedelta(minutes=i+1)
            daily_data.append({
                "time": forecast_time.isoformat(),
                "voltage": float(daily_forecast.iloc[i]),
                "confidence_lower": float(daily_conf_int.iloc[i, 0]),
                "confidence_upper": float(daily_conf_int.iloc[i, 1])
            })
        
        # Calculate forecast statistics
        current_voltage = float(voltage_series.iloc[-1])
        hourly_avg = float(hourly_forecast.mean())
        daily_avg = float(daily_forecast.mean())
        
        # Voltage trend analysis
        hourly_trend = "stable"
        daily_trend = "stable"
        
        if hourly_avg > current_voltage * 1.05:
            hourly_trend = "increasing"
        elif hourly_avg < current_voltage * 0.95:
            hourly_trend = "decreasing"
            
        if daily_avg > current_voltage * 1.05:
            daily_trend = "increasing"
        elif daily_avg < current_voltage * 0.95:
            daily_trend = "decreasing"
        
        return {
            "current_voltage": current_voltage,
            "forecast_timestamp": current_time.isoformat(),
            "model_info": {
                "aic": float(best_model.aic),
                "order": best_model.specification['order']
            },
            "hourly_forecast": {
                "data": hourly_data,
                "average": hourly_avg,
                "trend": hourly_trend,
                "min_voltage": float(hourly_forecast.min()),
                "max_voltage": float(hourly_forecast.max())
            },
            "daily_forecast": {
                "data": daily_data,
                "average": daily_avg,
                "trend": daily_trend,
                "min_voltage": float(daily_forecast.min()),
                "max_voltage": float(daily_forecast.max())
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating voltage forecast: {str(e)}")

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