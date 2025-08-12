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
from ..utils.netlogo import run_netlogo_simulation

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
    # Default growth rate so missing body won't 422, and clients can omit safely
    house_growth_rate: float = 0.05

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
        
        # Get averages
        avg_df = pd.read_sql_query("SELECT AVG(total_voltage) as avg_voltage, AVG(total_load) as avg_load, AVG(house_count) as avg_houses FROM grid_data", conn)
        
        conn.close()
        
        if latest_df.empty:
            return {
                "status": "warning",
                "total_records": 0,
                "latest_tick": 0,
                "averages": {"voltage": 0, "load": 0, "houses": 0},
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
        
        return {
            "status": status,
            "total_records": int(total_count),
            "latest_tick": int(latest_df['tick'].iloc[0]),
            "averages": {
                "voltage": float(avg_df['avg_voltage'].iloc[0]),
                "load": float(avg_df['avg_load'].iloc[0]),
                "houses": float(avg_df['avg_houses'].iloc[0])
            },
            "timestamp": pd.Timestamp.now().isoformat()
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
        model_path = os.path.join(project_dir, 'simulation', 'power_grid.nlogo')
        csv_path = os.path.join(project_dir, 'simulation', 'grid_data.csv')

        # Try to update NetLogo parameter if model file exists; otherwise continue
        if os.path.exists(model_path):
            try:
                with open(model_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                for i, line in enumerate(lines):
                    if line.startswith('set house-growth-rate'):
                        lines[i] = f'set house-growth-rate {params.house_growth_rate}\n'
                with open(model_path, 'w', encoding='utf-8') as f:
                    f.writelines(lines)
            except Exception:
                # Non-fatal: continue with simulation
                pass

        # Run NetLogo simulation
        run_netlogo_simulation()

        # If NetLogo produced a CSV, import it; otherwise netlogo util likely wrote to DB already
        if os.path.exists(csv_path):
            df = pd.read_csv(csv_path)
            with sqlite3.connect(get_database_path()) as conn:
                df.to_sql('grid_data', conn, if_exists='append', index=False)
        return {"status": "Simulation completed"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/forecast")
def get_forecast():
    try:
        models_path = get_models_path()
        svr = joblib.load(os.path.join(models_path, 'svr_model.pkl'))
        scaler = joblib.load(os.path.join(models_path, 'scaler.pkl'))
        arima = joblib.load(os.path.join(models_path, 'arima_model.pkl'))

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
    """Upload and process Excel file"""
    try:
        # Validate file type
        if not file.filename.endswith(('.xlsx', '.xls')):
            raise HTTPException(status_code=400, detail="Invalid file type. Please upload an Excel file.")
        
        # Read the Excel file
        contents = await file.read()
        
        try:
            # Try to read as Excel
            df = pd.read_excel(io.BytesIO(contents))
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to read Excel file: {str(e)}")
        
        # Validate required columns (adjust based on your needs)
        required_columns = ['voltage', 'load', 'houses']  # Example columns
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            raise HTTPException(
                status_code=400, 
                detail=f"Missing required columns: {', '.join(missing_columns)}"
            )
        
        # Process and store data (example - adjust based on your schema)
        conn = sqlite3.connect(get_database_path())
        
        # Convert DataFrame to match your schema
        processed_data = []
        for _, row in df.iterrows():
            processed_data.append({
                'tick': len(processed_data) + 1,
                'total_voltage': row.get('voltage', 0),
                'total_load': row.get('load', 0),
                'house_count': row.get('houses', 0),
                'timestamp': datetime.datetime.now().isoformat()
            })
        
        # Insert data into database
        processed_df = pd.DataFrame(processed_data)
        processed_df.to_sql('grid_data', conn, if_exists='append', index=False)
        conn.close()
        
        return {
            "message": "File uploaded and processed successfully",
            "rows_processed": len(processed_data),
            "filename": file.filename
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")

@router.get("/export-data")
async def export_data():
    """Export all system data as CSV"""
    try:
        conn = sqlite3.connect(get_database_path())
        
        # Get all data from database
        grid_data = pd.read_sql_query("SELECT * FROM grid_data ORDER BY tick", conn)
        
        # Get summary statistics
        summary_stats = pd.read_sql_query("""
            SELECT 
                COUNT(*) as total_records,
                AVG(total_voltage) as avg_voltage,
                AVG(total_load) as avg_load,
                AVG(house_count) as avg_houses,
                MIN(total_voltage) as min_voltage,
                MAX(total_voltage) as max_voltage,
                MIN(total_load) as min_load,
                MAX(total_load) as max_load
            FROM grid_data
        """, conn)
        
        conn.close()
        
        # Create CSV content
        output = io.StringIO()
        
        # Write summary section
        output.write("POWER GRID SYSTEM SUMMARY\n")
        output.write("=" * 50 + "\n")
        output.write(f"Export Date: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        output.write(f"Total Records: {summary_stats['total_records'].iloc[0]}\n")
        output.write(f"Average Voltage: {summary_stats['avg_voltage'].iloc[0]:.2f}V\n")
        output.write(f"Average Load: {summary_stats['avg_load'].iloc[0]:.2f}kW\n")
        output.write(f"Average Houses: {summary_stats['avg_houses'].iloc[0]:.0f}\n")
        output.write(f"Voltage Range: {summary_stats['min_voltage'].iloc[0]:.2f}V - {summary_stats['max_voltage'].iloc[0]:.2f}V\n")
        output.write(f"Load Range: {summary_stats['min_load'].iloc[0]:.2f}kW - {summary_stats['max_load'].iloc[0]:.2f}kW\n")
        output.write("\n")
        
        # Write detailed data section
        output.write("DETAILED GRID DATA\n")
        output.write("=" * 50 + "\n")
        
        # Convert DataFrame to CSV
        grid_data.to_csv(output, index=False)
        
        # Get the CSV content
        csv_content = output.getvalue()
        output.close()
        
        # Create response
        response = StreamingResponse(
            io.BytesIO(csv_content.encode('utf-8')),
            media_type='text/csv',
            headers={
                'Content-Disposition': f'attachment; filename="power_grid_export_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.csv"'
            }
        )
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error exporting data: {str(e)}")

@router.get("/data-statistics")
async def get_data_statistics():
    """Get statistics about the stored data"""
    try:
        # Use context manager to ensure connection closes on error as well
        with sqlite3.connect(get_database_path()) as conn:
            # Get basic statistics
            stats = pd.read_sql_query(
                """
                SELECT 
                    COUNT(*) as total_records,
                    MIN(created_at) as oldest_record,
                    MAX(created_at) as newest_record,
                    AVG(total_voltage) as avg_voltage,
                    AVG(total_load) as avg_load,
                    AVG(house_count) as avg_houses
                FROM grid_data
                """,
                conn,
            )
        
        if stats.empty or stats['total_records'].iloc[0] == 0:
            return {
                "total_records": 0,
                "oldest_record": None,
                "newest_record": None,
                "avg_voltage": 0,
                "avg_load": 0,
                "avg_houses": 0,
                "estimated_size": "0 KB"
            }
        
        # Estimate file size (rough calculation)
        estimated_size_kb = stats['total_records'].iloc[0] * 0.1  # Rough estimate
        size_unit = "KB"
        if estimated_size_kb > 1024:
            estimated_size_kb = estimated_size_kb / 1024
            size_unit = "MB"
        
        return {
            "total_records": int(stats['total_records'].iloc[0]),
            "oldest_record": stats['oldest_record'].iloc[0],
            "newest_record": stats['newest_record'].iloc[0],
            "avg_voltage": float(stats['avg_voltage'].iloc[0]),
            "avg_load": float(stats['avg_load'].iloc[0]),
            "avg_houses": float(stats['avg_houses'].iloc[0]),
            "estimated_size": f"{estimated_size_kb:.1f} {size_unit}"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting statistics: {str(e)}")