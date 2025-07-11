#!/usr/bin/env python3
"""
Train ML models for power grid forecasting
This script trains SVR and ARIMA models and saves them as pickle files.
"""

import pandas as pd
import numpy as np
import sqlite3
import joblib
import os
from sklearn.svm import SVR
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
from statsmodels.tsa.arima.model import ARIMA
import warnings
warnings.filterwarnings('ignore')

def train_models():
    """Train SVR and ARIMA models using grid data"""
    
    # Get the directory paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # The script is in backend directory, so use script_dir directly
    backend_dir = script_dir
    db_path = os.path.join(backend_dir, 'database.db')
    models_dir = os.path.join(backend_dir, 'models')
    
    # Ensure models directory exists
    os.makedirs(models_dir, exist_ok=True)
    
    print("Loading data from database...")
    
    try:
        # Load data from database
        conn = sqlite3.connect(db_path)
        df = pd.read_sql_query("SELECT * FROM grid_data ORDER BY tick", conn)
        conn.close()
        
        if df.empty:
            print("No data found in database. Run init_db.py first.")
            return False
            
        print(f"Loaded {len(df)} records from database")
        
        # Prepare features and target for SVR
        X = df[['total_voltage', 'house_count']]
        y = df['total_load']
        
        # Split data for training and testing
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Train SVR model
        print("Training SVR model...")
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        svr_model = SVR(kernel='rbf', C=100, gamma='scale')
        svr_model.fit(X_train_scaled, y_train)
        
        # Evaluate SVR model
        y_pred = svr_model.predict(X_test_scaled)
        svr_mse = mean_squared_error(y_test, y_pred)
        svr_r2 = r2_score(y_test, y_pred)
        
        print(f"SVR Model - MSE: {svr_mse:.2f}, R²: {svr_r2:.3f}")
        
        # Train ARIMA model
        print("Training ARIMA model...")
        # Use total_load as time series data
        ts_data = df['total_load'].values
        
        # Simple ARIMA model - adjust parameters based on your data
        arima_model = ARIMA(ts_data, order=(1, 1, 1))
        arima_fitted = arima_model.fit()
        
        print(f"ARIMA Model - AIC: {arima_fitted.aic:.2f}")
        
        # Save models
        print("Saving models...")
        
        # Save SVR model and scaler
        joblib.dump(svr_model, os.path.join(models_dir, 'svr_model.pkl'))
        joblib.dump(scaler, os.path.join(models_dir, 'scaler.pkl'))
        
        # Save ARIMA model
        joblib.dump(arima_fitted, os.path.join(models_dir, 'arima_model.pkl'))
        
        print("Models trained and saved successfully!")
        
        # Test loading the models
        print("Testing model loading...")
        loaded_svr = joblib.load(os.path.join(models_dir, 'svr_model.pkl'))
        loaded_scaler = joblib.load(os.path.join(models_dir, 'scaler.pkl'))
        loaded_arima = joblib.load(os.path.join(models_dir, 'arima_model.pkl'))
        
        # Make a test prediction
        test_input = [[22000, 100]]  # Example input
        test_scaled = loaded_scaler.transform(test_input)
        test_pred = loaded_svr.predict(test_scaled)
        
        print(f"Test SVR prediction: {test_pred[0]:.2f}")
        
        # Test ARIMA forecast
        arima_forecast = loaded_arima.forecast(steps=5)
        print(f"Test ARIMA forecast (5 steps): {arima_forecast.tolist()}")
        
        return True
        
    except Exception as e:
        print(f"Error training models: {e}")
        return False

if __name__ == "__main__":
    success = train_models()
    if success:
        print("Model training completed successfully!")
    else:
        print("Model training failed!")
