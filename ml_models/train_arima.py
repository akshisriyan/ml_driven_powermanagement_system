import pandas as pd
from statsmodels.tsa.arima.model import ARIMA
import joblib

# Load data
data = pd.read_csv('../simulation/grid_data.csv')
load_series = data['load']

# Train ARIMA model
model = ARIMA(load_series, order=(5,1,0))
model_fit = model.fit()

# Save model
joblib.dump(model_fit, '../backend/app/models/arima_model.pkl')

# Forecast next 10 steps
forecast = model_fit.forecast(steps=10)
print("ARIMA Forecast:", forecast)