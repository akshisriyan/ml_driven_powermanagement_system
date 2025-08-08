#!/usr/bin/env python3
"""
SVR Model Implementation for Power Grid Load Prediction
This file loads the pre-trained SVR model and provides load prediction functions.
"""

import joblib
import numpy as np
import pandas as pd
import os
from sklearn.svm import SVR
from sklearn.metrics import mean_squared_error, r2_score
import warnings
warnings.filterwarnings('ignore')

class SVRPredictor:
    def __init__(self, model_path=None, scaler_path=None):
        """
        Initialize SVR Predictor
        
        Args:
            model_path (str): Path to the saved SVR model pkl file
            scaler_path (str): Path to the saved scaler pkl file
        """
        script_dir = os.path.dirname(os.path.abspath(__file__))
        
        if model_path is None:
            model_path = os.path.join(script_dir, '..', 'backend', 'models', 'svr_model.pkl')
        if scaler_path is None:
            scaler_path = os.path.join(script_dir, '..', 'backend', 'models', 'scaler.pkl')
        
        self.model_path = model_path
        self.scaler_path = scaler_path
        self.model = None
        self.scaler = None
        self.feature_names = ['total_voltage', 'house_count']
        
        self.load_models()
    
    def load_models(self):
        """Load the pre-trained SVR model and scaler"""
        try:
            # Load SVR model
            self.model = joblib.load(self.model_path)
            print(f"✅ SVR model loaded successfully from {self.model_path}")
            print(f"📊 Model Info: {type(self.model).__name__}")
            print(f"🔧 Kernel: {self.model.kernel}")
            print(f"⚙️ C parameter: {self.model.C}")
            print(f"📏 Gamma: {self.model.gamma}")
            
            # Load scaler
            self.scaler = joblib.load(self.scaler_path)
            print(f"✅ Scaler loaded successfully from {self.scaler_path}")
            print(f"📊 Support Vectors: {self.model.n_support_}")
            
        except Exception as e:
            print(f"❌ Error loading models: {e}")
            raise
    
    def predict_load(self, voltage, house_count):
        """
        Predict power load for given voltage and house count
        
        Args:
            voltage (float): Total voltage value
            house_count (int): Number of houses
            
        Returns:
            float: Predicted load value
        """
        try:
            # Prepare input data
            input_data = np.array([[voltage, house_count]])
            
            # Scale the input
            scaled_input = self.scaler.transform(input_data)
            
            # Make prediction
            prediction = self.model.predict(scaled_input)
            
            return float(prediction[0])
        except Exception as e:
            print(f"❌ Error making prediction: {e}")
            return None
    
    def predict_batch(self, data):
        """
        Predict loads for multiple input samples
        
        Args:
            data: List of [voltage, house_count] pairs or numpy array
            
        Returns:
            list: Predicted load values
        """
        try:
            # Convert to numpy array
            if isinstance(data, list):
                data = np.array(data)
            
            # Scale the inputs
            scaled_data = self.scaler.transform(data)
            
            # Make predictions
            predictions = self.model.predict(scaled_data)
            
            return predictions.tolist()
        except Exception as e:
            print(f"❌ Error making batch predictions: {e}")
            return None
    
    def predict_with_confidence(self, voltage, house_count, n_estimations=100):
        """
        Predict load with confidence estimation using bootstrap-like approach
        
        Args:
            voltage (float): Total voltage value
            house_count (int): Number of houses
            n_estimations (int): Number of estimations for confidence
            
        Returns:
            dict: Prediction with confidence metrics
        """
        try:
            # Base prediction
            base_prediction = self.predict_load(voltage, house_count)
            
            # Create small variations around input for confidence estimation
            np.random.seed(42)
            voltage_variations = np.random.normal(voltage, voltage * 0.01, n_estimations)
            house_variations = np.random.normal(house_count, house_count * 0.05, n_estimations)
            
            variations = [[v, h] for v, h in zip(voltage_variations, house_variations)]
            variation_predictions = self.predict_batch(variations)
            
            if variation_predictions:
                std_dev = np.std(variation_predictions)
                confidence_interval = 1.96 * std_dev  # 95% confidence
                
                return {
                    'prediction': base_prediction,
                    'confidence_interval': confidence_interval,
                    'lower_bound': base_prediction - confidence_interval,
                    'upper_bound': base_prediction + confidence_interval,
                    'std_deviation': std_dev
                }
            else:
                return {'prediction': base_prediction}
                
        except Exception as e:
            print(f"❌ Error making confidence prediction: {e}")
            return None
    
    def get_model_info(self):
        """Get detailed model information"""
        if self.model and self.scaler:
            return {
                'model_type': 'Support Vector Regression (SVR)',
                'kernel': self.model.kernel,
                'C_parameter': self.model.C,
                'gamma': self.model.gamma,
                'epsilon': self.model.epsilon,
                'n_support_vectors': self.model.n_support_,
                'feature_names': self.feature_names,
                'scaler_mean': self.scaler.mean_.tolist(),
                'scaler_scale': self.scaler.scale_.tolist()
            }
        return None
    
    def simulate_grid_scenarios(self):
        """Simulate different grid scenarios and their predicted loads"""
        scenarios = [
            {'name': 'Low Demand', 'voltage': 21000, 'houses': 80},
            {'name': 'Normal Demand', 'voltage': 22500, 'houses': 110},
            {'name': 'High Demand', 'voltage': 24000, 'houses': 140},
            {'name': 'Peak Demand', 'voltage': 24500, 'houses': 150},
            {'name': 'Emergency Low', 'voltage': 20000, 'houses': 120},
        ]
        
        results = []
        for scenario in scenarios:
            prediction = self.predict_with_confidence(
                scenario['voltage'], 
                scenario['houses']
            )
            
            if prediction:
                results.append({
                    'scenario': scenario['name'],
                    'input': f"V={scenario['voltage']}, H={scenario['houses']}",
                    'predicted_load': prediction['prediction'],
                    'confidence_range': f"±{prediction.get('confidence_interval', 0):.2f}",
                    'load_range': f"{prediction.get('lower_bound', 0):.1f} - {prediction.get('upper_bound', 0):.1f}"
                })
        
        return results
    
    def evaluate_on_sample_data(self, n_samples=10):
        """Generate sample data and evaluate model performance"""
        np.random.seed(42)
        
        # Generate realistic test data
        voltages = np.random.uniform(20000, 25000, n_samples)
        house_counts = np.random.randint(80, 150, n_samples)
        
        # Create synthetic true loads (simplified relationship)
        true_loads = []
        for v, h in zip(voltages, house_counts):
            # Simplified load calculation for demonstration
            base_load = h * 7.5  # ~7.5 units per house
            voltage_factor = v / 22500  # normalize around 22500V
            true_load = base_load * voltage_factor + np.random.normal(0, 10)
            true_loads.append(true_load)
        
        # Predict using our model
        test_data = [[v, h] for v, h in zip(voltages, house_counts)]
        predictions = self.predict_batch(test_data)
        
        if predictions:
            # Calculate metrics
            mse = mean_squared_error(true_loads, predictions)
            r2 = r2_score(true_loads, predictions)
            
            return {
                'n_samples': n_samples,
                'mse': mse,
                'rmse': np.sqrt(mse),
                'r2_score': r2,
                'mean_absolute_error': np.mean(np.abs(np.array(true_loads) - np.array(predictions))),
                'sample_results': [
                    {
                        'voltage': v,
                        'houses': h,
                        'true_load': t,
                        'predicted_load': p,
                        'error': abs(t - p)
                    }
                    for v, h, t, p in zip(voltages[:5], house_counts[:5], true_loads[:5], predictions[:5])
                ]
            }
        
        return None

def main():
    """Demo function to show SVR model usage"""
    print("🔋 SVR Load Prediction Demo")
    print("=" * 50)
    
    # Initialize predictor
    predictor = SVRPredictor()
    
    # Get model info
    print("\n📊 Model Information:")
    info = predictor.get_model_info()
    for key, value in info.items():
        print(f"   {key}: {value}")
    
    # Single prediction
    print("\n🎯 Single Prediction:")
    voltage = 22500
    houses = 120
    prediction = predictor.predict_with_confidence(voltage, houses)
    if prediction:
        print(f"   Input: Voltage={voltage}V, Houses={houses}")
        print(f"   Predicted Load: {prediction['prediction']:.2f}")
        print(f"   Confidence Interval: ±{prediction.get('confidence_interval', 0):.2f}")
        print(f"   Range: {prediction.get('lower_bound', 0):.1f} - {prediction.get('upper_bound', 0):.1f}")
    
    # Batch predictions
    print("\n📦 Batch Predictions:")
    batch_data = [[21000, 100], [22500, 120], [24000, 140]]
    batch_predictions = predictor.predict_batch(batch_data)
    if batch_predictions:
        for i, (data, pred) in enumerate(zip(batch_data, batch_predictions)):
            print(f"   Sample {i+1}: V={data[0]}, H={data[1]} → Load={pred:.2f}")
    
    # Scenario simulation
    print("\n🌟 Grid Scenario Simulation:")
    scenarios = predictor.simulate_grid_scenarios()
    for scenario in scenarios:
        print(f"   {scenario['scenario']}:")
        print(f"     Input: {scenario['input']}")
        print(f"     Predicted Load: {scenario['predicted_load']:.2f}")
        print(f"     Range: {scenario['load_range']}")
    
    # Model evaluation
    print("\n📈 Model Evaluation on Sample Data:")
    evaluation = predictor.evaluate_on_sample_data(20)
    if evaluation:
        print(f"   Samples: {evaluation['n_samples']}")
        print(f"   RMSE: {evaluation['rmse']:.2f}")
        print(f"   R² Score: {evaluation['r2_score']:.3f}")
        print(f"   Mean Absolute Error: {evaluation['mean_absolute_error']:.2f}")
        
        print(f"\n   Sample Predictions:")
        for i, result in enumerate(evaluation['sample_results']):
            print(f"     {i+1}. V={result['voltage']:.0f}, H={result['houses']} → "
                  f"True={result['true_load']:.1f}, Pred={result['predicted_load']:.1f}, "
                  f"Error={result['error']:.1f}")

if __name__ == "__main__":
    main()
