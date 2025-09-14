import React, { useState, useEffect } from 'react';
import { gridService } from '../services/api';

const VoltageForecast = ({ loading }) => {
  const [forecastData, setForecastData] = useState(null);
  const [forecastSummary, setForecastSummary] = useState(null);
  const [error, setError] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [selectedHorizon, setSelectedHorizon] = useState('hourly');

  useEffect(() => {
    fetchForecastData();
    const interval = setInterval(fetchForecastData, 60000); // Update every minute
    return () => clearInterval(interval);
  }, []);

  const fetchForecastData = async () => {
    try {
      setIsLoading(true);
      setError(null);
      
      // Fetch both detailed forecast and summary
      const [detailedData, summaryData] = await Promise.all([
        gridService.getVoltageForecast(),
        gridService.getForecastSummary()
      ]);
      
      setForecastData(detailedData);
      setForecastSummary(summaryData);
    } catch (err) {
      console.error('Error fetching forecast data:', err);
      setError('Failed to load forecast data');
    } finally {
      setIsLoading(false);
    }
  };

  const formatVoltage = (voltage) => {
    // Backend now returns voltage in proper 220V range
    if (voltage > 1000) {
      // Legacy support: if we get old-style high values (22000V), divide by 1000  
      return `${(voltage / 1000).toFixed(1)}kV`;
    } else {
      // New format: voltage is already in proper range (220V), display as V instead of kV
      return `${voltage.toFixed(0)}V`;
    }
  };

  const formatTime = (timeString) => {
    const date = new Date(timeString);
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  const formatDate = (timeString) => {
    const date = new Date(timeString);
    return date.toLocaleDateString();
  };

  const getTrendIcon = (trend) => {
    switch (trend) {
      case 'increasing': return '📈';
      case 'decreasing': return '📉';
      default: return '➡️';
    }
  };

  const getTrendColor = (trend) => {
    switch (trend) {
      case 'increasing': return '#28a745';
      case 'decreasing': return '#dc3545';
      default: return '#6c757d';
    }
  };

  const getConfidenceColor = (confidence) => {
    if (confidence === 'high') return '#28a745';
    if (confidence === 'medium') return '#ffc107';
    return '#dc3545';
  };

  const renderForecastChart = (horizonData, horizonName) => {
    if (!horizonData || !horizonData.data || horizonData.data.length === 0) {
      return <div className="no-data">No forecast data available</div>;
    }

    const maxDataPoints = 20; // Limit display for performance
    const step = Math.max(1, Math.floor(horizonData.data.length / maxDataPoints));
    const displayData = horizonData.data.filter((_, index) => index % step === 0);

    return (
      <div className="forecast-chart">
        <div className="chart-header">
          <h4>{horizonName} Forecast</h4>
          <div className="forecast-stats">
            <span className="stat">
              Avg: {formatVoltage(horizonData.average)}
            </span>
            <span className="stat" style={{ color: getTrendColor(horizonData.trend) }}>
              {getTrendIcon(horizonData.trend)} {horizonData.trend}
            </span>
            <span className="stat">
              Range: {formatVoltage(horizonData.min_voltage)} - {formatVoltage(horizonData.max_voltage)}
            </span>
          </div>
        </div>
        <div className="chart-container">
          {displayData.map((point, index) => (
            <div key={index} className="chart-point">
              <div className="chart-bar">
                <div 
                  className="bar-fill"
                  style={{ 
                    height: `${Math.max(20, (point.voltage / 25000) * 100)}px`,
                    backgroundColor: point.voltage > horizonData.average ? '#28a745' : '#6c757d'
                  }}
                ></div>
              </div>
              <div className="chart-label">
                {horizonName.includes('Hour') ? formatTime(point.time) : formatDate(point.time)}
              </div>
              <div className="chart-value">
                {formatVoltage(point.voltage)}
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  };

  const renderEnvironmentalFactors = () => {
    if (!forecastData?.current_environment || Object.keys(forecastData.current_environment).length === 0) {
      return null;
    }

    const env = forecastData.current_environment;
    return (
      <div className="environmental-factors">
        <h4>🌍 Current Environmental Conditions</h4>
        <div className="env-grid">
          {env.temperature !== undefined && (
            <div className="env-item">
              <span className="env-icon">🌡️</span>
              <span className="env-label">Temperature</span>
              <span className="env-value">{env.temperature.toFixed(1)}°C</span>
            </div>
          )}
          {env.humidity !== undefined && (
            <div className="env-item">
              <span className="env-icon">💧</span>
              <span className="env-label">Humidity</span>
              <span className="env-value">{env.humidity.toFixed(1)}%</span>
            </div>
          )}
          {env.solar_intensity !== undefined && (
            <div className="env-item">
              <span className="env-icon">☀️</span>
              <span className="env-label">Solar</span>
              <span className="env-value">{env.solar_intensity.toFixed(1)}%</span>
            </div>
          )}
          {env.wind_speed !== undefined && (
            <div className="env-item">
              <span className="env-icon">💨</span>
              <span className="env-label">Wind</span>
              <span className="env-value">{env.wind_speed.toFixed(1)} m/s</span>
            </div>
          )}
          {env.peak_hours !== undefined && (
            <div className="env-item">
              <span className="env-icon">⚡</span>
              <span className="env-label">Peak Hours</span>
              <span className="env-value">{env.peak_hours ? 'Yes' : 'No'}</span>
            </div>
          )}
        </div>
      </div>
    );
  };

  if (isLoading && !forecastData) {
    return (
      <div className="card">
        <h2>⚡ Voltage Forecast</h2>
        <div className="loading-spinner">Loading forecast data...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="card">
        <h2>⚡ Voltage Forecast</h2>
        <div className="error-message">
          <p>{error}</p>
          <button onClick={fetchForecastData} className="btn-primary">
            Retry
          </button>
        </div>
      </div>
    );
  }

  const horizons = [
    { key: 'hourly', name: 'Next Hour', data: forecastData?.hourly_forecast },
    { key: 'daily', name: 'Next 24 Hours', data: forecastData?.daily_forecast },
    { key: 'monthly', name: 'Next 30 Days', data: forecastData?.monthly_forecast },
    { key: 'yearly', name: 'Next 12 Months', data: forecastData?.yearly_forecast }
  ];

  const selectedHorizonData = horizons.find(h => h.key === selectedHorizon);

  return (
    <div className="card">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
        <h2>⚡ Voltage Forecast</h2>
        <div style={{ fontSize: '0.9em', color: '#666' }}>
          Updated: {forecastData?.forecast_timestamp ? 
            new Date(forecastData.forecast_timestamp).toLocaleTimeString() : 'Unknown'}
        </div>
      </div>

      {/* Current Status */}
      <div className="forecast-summary">
        <h3>Current Status</h3>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem' }}>
          <div className="status-card">
            <div className="status-label">CURRENT VOLTAGE</div>
            <div className="status-value">
              {forecastData?.current_voltage ? formatVoltage(forecastData.current_voltage) : 'N/A'}
            </div>
          </div>
          <div className="status-card">
            <div className="status-label">FORECAST CONFIDENCE</div>
            <div className="status-value" style={{ color: getConfidenceColor(forecastSummary?.confidence || 'medium') }}>
              {forecastSummary?.confidence || 'medium'}
            </div>
          </div>
          <div className="status-card">
            <div className="status-label">MODEL TYPE</div>
            <div className="status-value" style={{ fontSize: '0.9em' }}>
              {forecastData?.model_info?.model_type || 'Standard ARIMA'}
            </div>
          </div>
          {forecastData?.model_info?.uses_environmental_factors && (
            <div className="status-card">
              <div className="status-label">ENVIRONMENTAL DATA</div>
              <div className="status-value" style={{ color: '#28a745' }}>
                ✓ Active
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Environmental Factors */}
      {renderEnvironmentalFactors()}

      {/* Horizon Selection */}
      <div className="horizon-selector">
        <h3>Forecast Horizons</h3>
        <div className="horizon-tabs">
          {horizons.map(horizon => (
            <button
              key={horizon.key}
              className={`horizon-tab ${selectedHorizon === horizon.key ? 'active' : ''}`}
              onClick={() => setSelectedHorizon(horizon.key)}
            >
              {horizon.name}
            </button>
          ))}
        </div>
      </div>

      {/* Selected Forecast Chart */}
      {selectedHorizonData && renderForecastChart(selectedHorizonData.data, selectedHorizonData.name)}

      {/* Quick Summary Cards */}
      <div className="predictions-summary">
        <h3>Quick Predictions</h3>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))', gap: '1rem' }}>
          {horizons.map(horizon => {
            if (!horizon.data) return null;
            return (
              <div key={horizon.key} className="prediction-card">
                <div className="prediction-icon">
                  {getTrendIcon(horizon.data.trend)}
                </div>
                <div className="prediction-value">
                  {formatVoltage(horizon.data.average)}
                </div>
                <div className="prediction-change" style={{ color: getTrendColor(horizon.data.trend) }}>
                  {horizon.data.trend}
                </div>
                <div className="prediction-label">{horizon.name}</div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Model Information */}
      {forecastData?.model_info && (
        <div className="model-info">
          <h4>📊 Model Information</h4>
          <div className="model-details">
            <span><strong>Type:</strong> {forecastData.model_info.model_type}</span>
            <span><strong>Environmental Factors:</strong> {forecastData.model_info.uses_environmental_factors ? 'Yes' : 'No'}</span>
            {forecastData.model_info.environmental_features && forecastData.model_info.environmental_features.length > 0 && (
              <span><strong>Features:</strong> {forecastData.model_info.environmental_features.join(', ')}</span>
            )}
            {forecastData.model_info.aic && (
              <span><strong>AIC Score:</strong> {forecastData.model_info.aic.toFixed(2)}</span>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default VoltageForecast;
