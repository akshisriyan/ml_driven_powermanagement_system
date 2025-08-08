# ML Power Grid Models - Python Implementation

This directory contains Python implementations for the three trained machine learning models used in the Power Grid Management System.

## 📁 Files Overview

### Core Model Files
- **`arima_model.py`** - ARIMA model for voltage forecasting
- **`scaler_model.py`** - StandardScaler for data preprocessing  
- **`svr_model.py`** - Support Vector Regression for load prediction
- **`complete_demo.py`** - Complete demonstration using all three models

### Model Dependencies
The models load pre-trained files from `../backend/models/`:
- `arima_model.pkl` - Trained ARIMA model
- `scaler.pkl` - Fitted StandardScaler
- `svr_model.pkl` - Trained SVR model

## 🚀 Quick Start

### Prerequisites
```bash
pip install joblib numpy pandas scikit-learn statsmodels
```

### Individual Model Usage

#### 1. ARIMA Voltage Forecasting
```python
from arima_model import ARIMAForecaster

# Initialize forecaster
forecaster = ARIMAForecaster()

# Get 1-hour forecast
forecast_1h = forecaster.forecast_1_hour()
print(f"Next hour voltage: {forecast_1h['forecast_values'][0]:.2f}V")

# Get 24-hour forecast
forecast_24h = forecaster.forecast_1_day()
print(f"24-hour average: {np.mean(forecast_24h['forecast_values']):.2f}V")

# Custom forecast
custom = forecaster.forecast_voltage(steps=10)
```

#### 2. Data Scaling/Preprocessing
```python
from scaler_model import GridDataScaler

# Initialize scaler
scaler = GridDataScaler()

# Normalize single data point
normalized = scaler.normalize_grid_data(voltage=22500, house_count=120)
print(f"Normalized: {normalized[0]}")

# Batch processing
batch_data = [[22000, 100], [23000, 110], [24000, 120]]
batch_normalized = scaler.transform(batch_data)

# Inverse transform
original = scaler.inverse_transform(normalized)
```

#### 3. SVR Load Prediction
```python
from svr_model import SVRPredictor

# Initialize predictor
predictor = SVRPredictor()

# Single prediction
load = predictor.predict_load(voltage=22500, house_count=120)
print(f"Predicted load: {load:.2f} units")

# Prediction with confidence
prediction = predictor.predict_with_confidence(22500, 120)
print(f"Load: {prediction['prediction']:.2f} ± {prediction['confidence_interval']:.2f}")

# Batch predictions
batch_data = [[21000, 100], [22500, 120], [24000, 140]]
predictions = predictor.predict_batch(batch_data)
```

### Complete Integration
```python
from complete_demo import PowerGridAnalyzer

# Initialize all models
analyzer = PowerGridAnalyzer()

# Comprehensive analysis
analysis = analyzer.comprehensive_analysis(voltage=22500, house_count=120)

# Compare multiple scenarios
scenarios = analyzer.scenario_comparison()

# Generate complete report
analyzer.generate_report(voltage=22500, house_count=120)
```

## 🔧 Model Details

### ARIMA Model
- **Purpose**: Voltage forecasting over time
- **Input**: Time series voltage data
- **Output**: Future voltage predictions with confidence intervals
- **Use Cases**: 
  - 1-hour voltage prediction
  - 24-hour voltage planning
  - Trend analysis

### StandardScaler
- **Purpose**: Data normalization and preprocessing
- **Input**: Raw voltage and house count data
- **Output**: Scaled/normalized data for ML models
- **Features**: 
  - Transform to standard scale
  - Inverse transform to original scale
  - Batch processing support

### SVR Model
- **Purpose**: Load prediction based on voltage and house count
- **Input**: [voltage, house_count] (scaled)
- **Output**: Predicted power load
- **Features**:
  - RBF kernel for non-linear relationships
  - Confidence estimation
  - Scenario analysis

## 📊 Example Outputs

### ARIMA Forecast
```json
{
  "timestamps": ["2025-08-08T18:00:00", "2025-08-08T19:00:00"],
  "forecast_values": [22456.78, 22489.23],
  "lower_ci": [22156.45, 22189.12],
  "upper_ci": [22757.11, 22789.34],
  "steps": 2
}
```

### SVR Prediction
```json
{
  "prediction": 875.42,
  "confidence_interval": 23.15,
  "lower_bound": 852.27,
  "upper_bound": 898.57
}
```

## 🎯 Practical Applications

### Real-time Monitoring
- Load current grid data into models
- Get immediate load predictions
- Monitor voltage trends

### Capacity Planning
- Forecast voltage for next 24 hours
- Predict load requirements
- Plan generation capacity

### Anomaly Detection
- Compare predictions with actual values
- Identify unusual patterns
- Alert for potential issues

### Optimization
- Test different operational scenarios
- Optimize load distribution
- Minimize energy waste

## 🔍 Running the Demo

Execute the complete demonstration:
```bash
python complete_demo.py
```

This will show:
- Model loading and initialization
- Single point analysis
- Scenario comparison
- Detailed forecasting
- Comprehensive reporting

## 📈 Model Performance

The models are trained on power grid simulation data and provide:
- **ARIMA**: Time series forecasting with confidence intervals
- **SVR**: Load prediction with R² score and confidence estimation  
- **Scaler**: Proper normalization for optimal model performance

## 🛠️ Customization

You can modify the model implementations to:
- Change forecast horizons
- Adjust confidence levels
- Add new scenarios
- Integrate with real-time data sources
- Export results to different formats

## 📝 Notes

- Ensure the backend/models directory contains the .pkl files
- Models are pre-trained and ready to use
- Each model file can be run independently for testing
- The complete_demo.py provides comprehensive usage examples

## 🔗 Integration with Main System

These models are the same ones used by the web dashboard backend. You can:
- Use them for offline analysis
- Integrate with external systems
- Develop custom applications
- Create automated monitoring scripts

---

**Ready to analyze your power grid data! 🚀⚡**
