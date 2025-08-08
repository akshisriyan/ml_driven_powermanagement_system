#!/usr/bin/env python3
"""
ARIMA Model Implementation for Power Grid Voltage Forecasting
This file loads the pre-trained ARIMA model and provides forecasting functions.
"""

import joblib
import numpy as np
import pandas as pd
import os
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

class ARIMAForecaster:
    def __init__(self, model_path=None):
        """
        Initialize ARIMA Forecaster
        
        Args:
            model_path (str): Path to the saved ARIMA model pkl file
        """
        if model_path is None:
            # Default path to the backend models directory
            script_dir = os.path.dirname(os.path.abspath(__file__))
            model_path = os.path.join(script_dir, '..', 'backend', 'models', 'arima_model.pkl')
        
        self.model_path = model_path
        self.model = None
        self.load_model()
    
    def load_model(self):
        """Load the pre-trained ARIMA model"""
        try:
            self.model = joblib.load(self.model_path)
            print(f"✅ ARIMA model loaded successfully from {self.model_path}")
            print(f"📊 Model Info: {self.model.model}")
            print(f"📈 AIC: {self.model.aic:.2f}")
        except Exception as e:
            print(f"❌ Error loading ARIMA model: {e}")
            raise
    
    def forecast_voltage(self, steps=5):
        """
        Forecast voltage for the next n steps
        
        Args:
            steps (int): Number of future steps to forecast
            
        Returns:
            dict: Forecast results with values and confidence intervals
        """
        try:
            # Get forecast with confidence intervals
            forecast = self.model.forecast(steps=steps)
            forecast_ci = self.model.get_forecast(steps=steps).conf_int()
            
            # Create timestamps for forecast
            timestamps = []
            base_time = datetime.now()
            for i in range(steps):
                timestamps.append((base_time + timedelta(hours=i+1)).isoformat())
            
            result = {
                'timestamps': timestamps,
                'forecast_values': forecast.tolist(),
                'lower_ci': forecast_ci.iloc[:, 0].tolist(),
                'upper_ci': forecast_ci.iloc[:, 1].tolist(),
                'steps': steps,
                'model_type': 'ARIMA',
                'forecast_time': datetime.now().isoformat()
            }
            
            return result
        except Exception as e:
            print(f"❌ Error making forecast: {e}")
            return None
    
    def forecast_1_hour(self):
        """Quick forecast for next 1 hour"""
        return self.forecast_voltage(steps=1)
    
    def forecast_1_day(self):
        """Quick forecast for next 24 hours"""
        return self.forecast_voltage(steps=24)
    
    def get_model_summary(self):
        """Get detailed model summary"""
        if self.model:
            return {
                'model_type': 'ARIMA',
                'order': str(self.model.model.order),
                'aic': self.model.aic,
                'bic': self.model.bic,
                'log_likelihood': self.model.llf,
                'observations': self.model.nobs,
                'parameters': self.model.params.to_dict()
            }
        return None

def main():
    """Demo function to show ARIMA model usage"""
    print("🔋 ARIMA Voltage Forecasting Demo")
    print("=" * 50)
    
    # Initialize forecaster
    forecaster = ARIMAForecaster()
    
    # Get model summary
    print("\n📊 Model Summary:")
    summary = forecaster.get_model_summary()
    for key, value in summary.items():
        print(f"   {key}: {value}")
    
    # Make 1-hour forecast
    print("\n⏰ 1-Hour Forecast:")
    forecast_1h = forecaster.forecast_1_hour()
    if forecast_1h:
        print(f"   Predicted Voltage: {forecast_1h['forecast_values'][0]:.2f}")
        print(f"   Confidence Interval: [{forecast_1h['lower_ci'][0]:.2f}, {forecast_1h['upper_ci'][0]:.2f}]")
    
    # Make 1-day forecast
    print("\n📅 24-Hour Forecast:")
    forecast_24h = forecaster.forecast_1_day()
    if forecast_24h:
        print(f"   First 5 hours forecast:")
        for i in range(min(5, len(forecast_24h['forecast_values']))):
            print(f"   Hour {i+1}: {forecast_24h['forecast_values'][i]:.2f} ± {(forecast_24h['upper_ci'][i] - forecast_24h['lower_ci'][i])/2:.2f}")
    
    # Make custom forecast
    print("\n🔮 Custom 10-Step Forecast:")
    custom_forecast = forecaster.forecast_voltage(steps=10)
    if custom_forecast:
        print(f"   Average forecasted value: {np.mean(custom_forecast['forecast_values']):.2f}")
        print(f"   Forecast range: {min(custom_forecast['forecast_values']):.2f} - {max(custom_forecast['forecast_values']):.2f}")

if __name__ == "__main__":
    main()
