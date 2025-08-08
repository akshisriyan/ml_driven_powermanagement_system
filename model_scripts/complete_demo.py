#!/usr/bin/env python3
"""
Complete Model Demo - Using ARIMA, Scaler, and SVR Models Together
This file demonstrates how to use all three trained models for comprehensive power grid analysis.
"""

import os
import sys
import numpy as np
from datetime import datetime

# Add the current directory to Python path to import our model modules
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

# Import our custom model classes
try:
    from arima_model import ARIMAForecaster
    from scaler_model import GridDataScaler
    from svr_model import SVRPredictor
except ImportError as e:
    print(f"❌ Error importing model modules: {e}")
    print("Please ensure all model files are in the same directory")
    sys.exit(1)

class PowerGridAnalyzer:
    """Complete power grid analysis using all three models"""
    
    def __init__(self):
        """Initialize all models"""
        print("🚀 Initializing Power Grid Analyzer...")
        print("=" * 60)
        
        try:
            self.arima_forecaster = ARIMAForecaster()
            self.scaler = GridDataScaler()
            self.svr_predictor = SVRPredictor()
            print("\n✅ All models loaded successfully!")
        except Exception as e:
            print(f"❌ Error initializing models: {e}")
            raise
    
    def comprehensive_analysis(self, voltage=22500, house_count=120):
        """
        Perform comprehensive grid analysis
        
        Args:
            voltage (float): Current voltage
            house_count (int): Number of houses
        """
        print(f"\n🔍 Comprehensive Power Grid Analysis")
        print(f"📊 Input Parameters: Voltage={voltage}V, Houses={house_count}")
        print("=" * 60)
        
        # 1. Current Load Prediction using SVR
        print("\n1️⃣ CURRENT LOAD PREDICTION (SVR)")
        print("-" * 40)
        current_load = self.svr_predictor.predict_with_confidence(voltage, house_count)
        if current_load:
            print(f"   💡 Predicted Current Load: {current_load['prediction']:.2f} units")
            print(f"   📊 Confidence Range: {current_load.get('lower_bound', 0):.1f} - {current_load.get('upper_bound', 0):.1f} units")
            print(f"   🎯 Accuracy: ±{current_load.get('confidence_interval', 0):.2f} units")
        
        # 2. Data Scaling and Normalization
        print("\n2️⃣ DATA PREPROCESSING (SCALER)")
        print("-" * 40)
        normalized_data = self.scaler.normalize_grid_data(voltage, house_count)
        if normalized_data is not None:
            print(f"   📥 Original Data: [Voltage={voltage}, Houses={house_count}]")
            print(f"   🔄 Normalized Data: [{normalized_data[0][0]:.3f}, {normalized_data[0][1]:.3f}]")
            
            # Show scaler statistics
            stats = self.scaler.get_scaler_stats()
            print(f"   📊 Scaling Statistics:")
            print(f"      Mean: {stats['mean_values']}")
            print(f"      Scale: {stats['scale_values']}")
        
        # 3. Voltage Forecasting using ARIMA
        print("\n3️⃣ VOLTAGE FORECASTING (ARIMA)")
        print("-" * 40)
        
        # 1-hour forecast
        forecast_1h = self.arima_forecaster.forecast_1_hour()
        if forecast_1h:
            print(f"   ⏰ 1-Hour Forecast:")
            print(f"      Predicted Voltage: {forecast_1h['forecast_values'][0]:.2f}V")
            print(f"      Confidence Range: {forecast_1h['lower_ci'][0]:.2f} - {forecast_1h['upper_ci'][0]:.2f}V")
        
        # 24-hour forecast
        forecast_24h = self.arima_forecaster.forecast_1_day()
        if forecast_24h:
            print(f"   📅 24-Hour Forecast Summary:")
            avg_voltage = np.mean(forecast_24h['forecast_values'])
            min_voltage = min(forecast_24h['forecast_values'])
            max_voltage = max(forecast_24h['forecast_values'])
            print(f"      Average Voltage: {avg_voltage:.2f}V")
            print(f"      Voltage Range: {min_voltage:.2f} - {max_voltage:.2f}V")
            print(f"      First 6 hours: {forecast_24h['forecast_values'][:6]}")
        
        return {
            'current_load': current_load,
            'normalized_data': normalized_data,
            'forecast_1h': forecast_1h,
            'forecast_24h': forecast_24h
        }
    
    def scenario_comparison(self):
        """Compare different grid scenarios"""
        print(f"\n🔄 SCENARIO COMPARISON")
        print("=" * 60)
        
        scenarios = [
            {'name': 'Low Demand Period', 'voltage': 21500, 'houses': 90},
            {'name': 'Normal Operation', 'voltage': 22500, 'houses': 120},
            {'name': 'High Demand Period', 'voltage': 23500, 'houses': 140},
            {'name': 'Peak Load Condition', 'voltage': 24000, 'houses': 160},
            {'name': 'Emergency Condition', 'voltage': 20500, 'houses': 100}
        ]
        
        results = []
        for i, scenario in enumerate(scenarios, 1):
            print(f"\n{i}️⃣ {scenario['name'].upper()}")
            print("-" * 40)
            
            # SVR Prediction
            load_pred = self.svr_predictor.predict_load(scenario['voltage'], scenario['houses'])
            
            # Data normalization
            norm_data = self.scaler.normalize_grid_data(scenario['voltage'], scenario['houses'])
            
            result = {
                'scenario': scenario['name'],
                'voltage': scenario['voltage'],
                'houses': scenario['houses'],
                'predicted_load': load_pred,
                'normalized': norm_data[0].tolist() if norm_data is not None else None
            }
            results.append(result)
            
            print(f"   🏠 Houses: {scenario['houses']}")
            print(f"   ⚡ Voltage: {scenario['voltage']}V")
            print(f"   💡 Predicted Load: {load_pred:.2f} units" if load_pred else "   ❌ Prediction failed")
            if norm_data is not None:
                print(f"   🔄 Normalized: [{norm_data[0][0]:.3f}, {norm_data[0][1]:.3f}]")
        
        return results
    
    def forecast_analysis(self):
        """Detailed forecast analysis"""
        print(f"\n📈 DETAILED FORECAST ANALYSIS")
        print("=" * 60)
        
        # Get various forecast horizons
        forecast_horizons = [1, 6, 12, 24, 48]  # hours
        
        for hours in forecast_horizons:
            print(f"\n⏱️ {hours}-Hour Forecast:")
            print("-" * 30)
            
            forecast = self.arima_forecaster.forecast_voltage(steps=hours)
            if forecast:
                values = forecast['forecast_values']
                lower_ci = forecast['lower_ci']
                upper_ci = forecast['upper_ci']
                
                print(f"   📊 Summary Statistics:")
                print(f"      Mean: {np.mean(values):.2f}V")
                print(f"      Std Dev: {np.std(values):.2f}V")
                print(f"      Range: {min(values):.2f} - {max(values):.2f}V")
                
                if hours <= 6:  # Show individual values for short forecasts
                    print(f"   📋 Individual Predictions:")
                    for i, (val, low, high) in enumerate(zip(values, lower_ci, upper_ci)):
                        print(f"      Hour {i+1}: {val:.2f}V (CI: {low:.2f} - {high:.2f})")
    
    def generate_report(self, voltage=22500, house_count=120):
        """Generate a comprehensive analysis report"""
        print(f"\n📋 POWER GRID ANALYSIS REPORT")
        print(f"🕐 Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 70)
        
        # Perform analysis
        analysis = self.comprehensive_analysis(voltage, house_count)
        
        # Additional insights
        print(f"\n💡 INSIGHTS AND RECOMMENDATIONS")
        print("-" * 50)
        
        if analysis['current_load']:
            load = analysis['current_load']['prediction']
            if load > 1000:
                print("   🔴 HIGH LOAD WARNING: Consider load balancing")
            elif load < 500:
                print("   🟡 LOW LOAD: Opportunity for energy optimization")
            else:
                print("   🟢 NORMAL LOAD: Operating within acceptable range")
        
        if analysis['forecast_24h']:
            voltages = analysis['forecast_24h']['forecast_values']
            voltage_trend = np.polyfit(range(len(voltages)), voltages, 1)[0]
            if voltage_trend > 10:
                print("   📈 VOLTAGE TRENDING UP: Monitor for stability")
            elif voltage_trend < -10:
                print("   📉 VOLTAGE TRENDING DOWN: Check generation capacity")
            else:
                print("   ➡️ VOLTAGE STABLE: Normal operation expected")
        
        print(f"\n🎯 OPERATIONAL RECOMMENDATIONS:")
        print("   1. Monitor load predictions for next 6 hours")
        print("   2. Adjust generation based on voltage forecasts")
        print("   3. Prepare for demand changes in peak hours")
        print("   4. Check equipment status if predictions show anomalies")

def main():
    """Main demo function"""
    print("🌟 POWER GRID ML MODELS DEMONSTRATION")
    print("🔋 ARIMA + SCALER + SVR Integration")
    print("=" * 70)
    
    try:
        # Initialize analyzer
        analyzer = PowerGridAnalyzer()
        
        # Test with current conditions
        print(f"\n🧪 TESTING WITH CURRENT CONDITIONS")
        analyzer.comprehensive_analysis(voltage=22750, house_count=125)
        
        # Compare scenarios
        analyzer.scenario_comparison()
        
        # Detailed forecasting
        analyzer.forecast_analysis()
        
        # Generate complete report
        analyzer.generate_report(voltage=22750, house_count=125)
        
        print(f"\n✅ DEMONSTRATION COMPLETED SUCCESSFULLY!")
        print("🔧 You can now use these models individually or together for your power grid analysis")
        
    except Exception as e:
        print(f"❌ Error during demonstration: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
