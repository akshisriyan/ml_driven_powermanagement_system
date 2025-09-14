import React, { useState, useEffect } from 'react';
import { gridService } from '../services/api';

const VoltageForecast = ({ loading }) => {
  const [forecastData, setForecastData] = useState(null);
  const [forecastSummary, setForecastSummary] = useState(null);
  const [error, setError] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

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
      // New format: voltage is already in proper range (220V), display as V
      return `${voltage.toFixed(0)}V`;
    }
  };

  const formatTime = (timeString) => {
    const date = new Date(timeString);
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  const getTrendIcon = (trend) => {
    switch (trend) {
      case 'increasing': return '📈';
      case 'decreasing': return '📉';
      default: return '➡️';
    }
  };

  const getAlertColor = (severity) => {
    switch (severity) {
      case 'high': return '#ff4444';
      case 'medium': return '#ff8800';
      case 'low': return '#4488ff';
      default: return '#888888';
    }
  };

  if (isLoading && !forecastData) {
    return (
      <div className="forecast-container">
        <div className="forecast-header">
          <h3>⚡ Voltage Forecast</h3>
        </div>
        <div className="forecast-loading">
          <div className="loading-spinner"></div>
          <p>Generating ARIMA forecast...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="forecast-container">
        <div className="forecast-header">
          <h3>⚡ Voltage Forecast</h3>
        </div>
        <div className="forecast-error">
          <p>⚠️ {error}</p>
          <button onClick={fetchForecastData} className="retry-button">
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="forecast-container">
      <div className="forecast-header">
        <h3>⚡ Voltage Forecast</h3>
        <p className="forecast-timestamp">
          Updated: {forecastSummary?.forecast_timestamp ? 
            new Date(forecastSummary.forecast_timestamp).toLocaleTimeString() : 
            'Loading...'
          }
        </p>
      </div>

      {/* Current Status */}
      <div className="current-status">
        <h4>Current Status</h4>
        <div className="status-grid">
          <div className="status-item">
            <span className="status-label">Current Voltage</span>
            <span className="status-value">
              {forecastSummary?.current_voltage ? 
                formatVoltage(forecastSummary.current_voltage) : 
                'Loading...'
              }
            </span>
          </div>
          <div className="status-item">
            <span className="status-label">Forecast Confidence</span>
            <span className="status-value">
              {forecastSummary?.confidence || 'Medium'}
            </span>
          </div>
        </div>
      </div>

      {/* Forecast Predictions */}
      {forecastSummary?.predictions && (
        <div className="predictions-section">
          <h4>Predictions</h4>
          <div className="predictions-grid">
            <div className="prediction-card">
              <div className="prediction-header">
                <h5>Next Hour</h5>
                <span className="trend-icon">
                  {getTrendIcon(forecastSummary.predictions.next_hour.trend)}
                </span>
              </div>
              <div className="prediction-content">
                <div className="prediction-value">
                  {formatVoltage(forecastSummary.predictions.next_hour.average_voltage)}
                </div>
                <div className="prediction-change">
                  {forecastSummary.predictions.next_hour.change_percentage > 0 ? '+' : ''}
                  {forecastSummary.predictions.next_hour.change_percentage.toFixed(1)}%
                </div>
              </div>
            </div>

            <div className="prediction-card">
              <div className="prediction-header">
                <h5>Next 24 Hours</h5>
                <span className="trend-icon">
                  {getTrendIcon(forecastSummary.predictions.next_day.trend)}
                </span>
              </div>
              <div className="prediction-content">
                <div className="prediction-value">
                  {formatVoltage(forecastSummary.predictions.next_day.average_voltage)}
                </div>
                <div className="prediction-change">
                  {forecastSummary.predictions.next_day.change_percentage > 0 ? '+' : ''}
                  {forecastSummary.predictions.next_day.change_percentage.toFixed(1)}%
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Alerts */}
      {forecastSummary?.alerts && forecastSummary.alerts.length > 0 && (
        <div className="alerts-section">
          <h4>Forecast Alerts</h4>
          <div className="alerts-list">
            {forecastSummary.alerts.map((alert, index) => (
              <div 
                key={index} 
                className="alert-item"
                style={{ borderLeftColor: getAlertColor(alert.severity) }}
              >
                <div className="alert-content">
                  <span className="alert-type">{alert.type.toUpperCase()}</span>
                  <span className="alert-message">{alert.message}</span>
                </div>
                <div className="alert-severity">{alert.severity}</div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Detailed Forecast Chart */}
      {forecastData?.hourly_forecast && (
        <div className="forecast-chart">
          <h4>Hourly Forecast (Next 60 Minutes)</h4>
          <div className="chart-container">
            <div className="chart-grid">
              {forecastData.hourly_forecast.data.slice(0, 12).map((point, index) => (
                <div key={index} className="chart-point">
                  <div className="chart-time">{formatTime(point.time)}</div>
                  <div className="chart-bar">
                    <div 
                      className="chart-fill"
                      style={{ 
                        height: `${Math.max(10, (point.voltage / 25000) * 100)}%`,
                        background: `linear-gradient(135deg, #00ffff, #8a2be2)`
                      }}
                    ></div>
                  </div>
                  <div className="chart-value">{formatVoltage(point.voltage)}</div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Model Information */}
      {forecastData?.model_info && (
        <div className="model-info">
          <h4>Model Information</h4>
          <div className="model-details">
            <span>ARIMA Order: ({forecastData.model_info.order.join(', ')})</span>
            <span>AIC: {forecastData.model_info.aic.toFixed(2)}</span>
          </div>
        </div>
      )}
    </div>
  );
};

export default VoltageForecast;
