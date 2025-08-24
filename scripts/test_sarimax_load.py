import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from ml_models.sarimax_forecaster import SARIMAXForecaster


f = SARIMAXForecaster()
print('Model path:', f.model_path)
print('Scaler path:', f.scaler_path)
try:
    out = f.forecast(steps=5)
    print('Forecast output:', out)
except Exception as e:
    import traceback
    traceback.print_exc()
    print('Forecast raised:', e)
