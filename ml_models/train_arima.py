import pandas as pd
from statsmodels.tsa.arima.model import ARIMA
import joblib
import os
import sqlite3

# Load data from SQLite
backend_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'backend')
db_path = os.path.join(backend_dir, 'database.db')
conn = sqlite3.connect(db_path)
data = pd.read_sql_query("SELECT total_load FROM grid_data ORDER BY tick", conn)
conn.close()
load_series = data['total_load']

# Train ARIMA model
model = ARIMA(load_series, order=(5,1,0))
model_fit = model.fit()

# Save model
models_dir = os.path.join(backend_dir, 'app', 'models')
os.makedirs(models_dir, exist_ok=True)
joblib.dump(model_fit, os.path.join(models_dir, 'arima_model.pkl'))

# Forecast next 10 steps
forecast = model_fit.forecast(steps=10)
print("ARIMA Forecast:", forecast)