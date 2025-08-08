#!/usr/bin/env python3
"""
Scaler Model Implementation for Power Grid Data Preprocessing
This file loads the pre-trained StandardScaler and provides data preprocessing functions.
"""

import joblib
import numpy as np
import pandas as pd
import os
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings('ignore')

class GridDataScaler:
    def __init__(self, scaler_path=None):
        """
        Initialize Grid Data Scaler
        
        Args:
            scaler_path (str): Path to the saved scaler pkl file
        """
        if scaler_path is None:
            # Default path to the backend models directory
            script_dir = os.path.dirname(os.path.abspath(__file__))
            scaler_path = os.path.join(script_dir, '..', 'backend', 'models', 'scaler.pkl')
        
        self.scaler_path = scaler_path
        self.scaler = None
        self.feature_names = ['total_voltage', 'house_count']
        self.load_scaler()
    
    def load_scaler(self):
        """Load the pre-trained StandardScaler"""
        try:
            self.scaler = joblib.load(self.scaler_path)
            print(f"✅ Scaler loaded successfully from {self.scaler_path}")
            print(f"📊 Scaler Info: {type(self.scaler).__name__}")
            print(f"🔢 Features: {len(self.scaler.mean_)} features")
            print(f"📈 Mean values: {self.scaler.mean_}")
            print(f"📊 Scale values: {self.scaler.scale_}")
        except Exception as e:
            print(f"❌ Error loading scaler: {e}")
            raise
    
    def transform(self, data):
        """
        Transform/normalize input data using the pre-trained scaler
        
        Args:
            data: Input data (can be list, numpy array, or pandas DataFrame)
            
        Returns:
            numpy.ndarray: Scaled/normalized data
        """
        try:
            # Convert to numpy array if needed
            if isinstance(data, list):
                data = np.array(data)
            elif isinstance(data, pd.DataFrame):
                data = data.values
            
            # Ensure 2D array
            if data.ndim == 1:
                data = data.reshape(1, -1)
            
            # Apply scaling
            scaled_data = self.scaler.transform(data)
            
            return scaled_data
        except Exception as e:
            print(f"❌ Error transforming data: {e}")
            return None
    
    def inverse_transform(self, scaled_data):
        """
        Convert scaled data back to original scale
        
        Args:
            scaled_data: Scaled/normalized data
            
        Returns:
            numpy.ndarray: Data in original scale
        """
        try:
            # Convert to numpy array if needed
            if isinstance(scaled_data, list):
                scaled_data = np.array(scaled_data)
            
            # Ensure 2D array
            if scaled_data.ndim == 1:
                scaled_data = scaled_data.reshape(1, -1)
            
            # Apply inverse scaling
            original_data = self.scaler.inverse_transform(scaled_data)
            
            return original_data
        except Exception as e:
            print(f"❌ Error inverse transforming data: {e}")
            return None
    
    def normalize_grid_data(self, voltage, house_count):
        """
        Normalize grid data (voltage and house count)
        
        Args:
            voltage (float): Total voltage value
            house_count (int): Number of houses
            
        Returns:
            numpy.ndarray: Normalized data ready for ML model input
        """
        data = [[voltage, house_count]]
        return self.transform(data)
    
    def denormalize_predictions(self, predictions, feature_index=None):
        """
        Convert normalized predictions back to original scale
        
        Args:
            predictions: Normalized prediction values
            feature_index: If predictions are for specific features
            
        Returns:
            Original scale predictions
        """
        if feature_index is not None:
            # Create dummy array with zeros and insert predictions
            dummy_data = np.zeros((len(predictions), len(self.scaler.mean_)))
            dummy_data[:, feature_index] = predictions
            denormalized = self.inverse_transform(dummy_data)
            return denormalized[:, feature_index]
        else:
            return self.inverse_transform(predictions)
    
    def get_scaler_stats(self):
        """Get scaler statistics"""
        if self.scaler:
            return {
                'scaler_type': type(self.scaler).__name__,
                'n_features': len(self.scaler.mean_),
                'feature_names': self.feature_names,
                'mean_values': self.scaler.mean_.tolist(),
                'scale_values': self.scaler.scale_.tolist(),
                'variance_values': self.scaler.var_.tolist() if hasattr(self.scaler, 'var_') else None
            }
        return None
    
    def create_sample_data(self, n_samples=5):
        """Create sample normalized data for testing"""
        np.random.seed(42)
        
        # Generate random data in typical ranges
        voltages = np.random.uniform(20000, 25000, n_samples)
        house_counts = np.random.randint(80, 150, n_samples)
        
        sample_data = []
        for v, h in zip(voltages, house_counts):
            original = [v, h]
            normalized = self.normalize_grid_data(v, h)[0]
            sample_data.append({
                'original': original,
                'normalized': normalized.tolist(),
                'voltage': v,
                'house_count': h
            })
        
        return sample_data

def main():
    """Demo function to show Scaler usage"""
    print("⚖️ Grid Data Scaler Demo")
    print("=" * 50)
    
    # Initialize scaler
    scaler = GridDataScaler()
    
    # Get scaler statistics
    print("\n📊 Scaler Statistics:")
    stats = scaler.get_scaler_stats()
    for key, value in stats.items():
        print(f"   {key}: {value}")
    
    # Test with sample data
    print("\n🧪 Sample Data Transformation:")
    sample_voltage = 22500.0
    sample_house_count = 120
    
    # Normalize
    normalized = scaler.normalize_grid_data(sample_voltage, sample_house_count)
    print(f"   Original: [voltage={sample_voltage}, houses={sample_house_count}]")
    print(f"   Normalized: {normalized[0]}")
    
    # Denormalize back
    denormalized = scaler.inverse_transform(normalized)
    print(f"   Denormalized: {denormalized[0]}")
    
    # Create and test multiple samples
    print("\n📋 Multiple Sample Processing:")
    samples = scaler.create_sample_data(3)
    for i, sample in enumerate(samples):
        print(f"   Sample {i+1}:")
        print(f"     Original: V={sample['voltage']:.1f}, H={sample['house_count']}")
        print(f"     Normalized: [{sample['normalized'][0]:.3f}, {sample['normalized'][1]:.3f}]")
    
    # Test batch processing
    print("\n📦 Batch Processing Test:")
    batch_data = [[22000, 100], [23000, 110], [24000, 120]]
    batch_normalized = scaler.transform(batch_data)
    print(f"   Batch input: {batch_data}")
    print(f"   Batch normalized:")
    for i, norm in enumerate(batch_normalized):
        print(f"     Sample {i+1}: [{norm[0]:.3f}, {norm[1]:.3f}]")

if __name__ == "__main__":
    main()
