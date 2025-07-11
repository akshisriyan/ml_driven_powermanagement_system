import React from 'react';

const ModelPredictions = ({ forecastData, loading }) => {
  if (loading) {
    return (
      <div className="model-predictions">
        <div className="predictions-header">
          <h3>🤖 ML Model Predictions</h3>
        </div>
        <div className="predictions-content loading">
          <div className="prediction-card skeleton">
            <div className="prediction-header skeleton"></div>
            <div className="prediction-body skeleton"></div>
          </div>
        </div>
      </div>
    );
  }

  const svr_prediction = forecastData?.svr_prediction || 0;
  const arima_prediction = forecastData?.arima_prediction || 0;
  const ensemble_prediction = forecastData?.ensemble_prediction || 0;
  const confidence = forecastData?.confidence || 0;

  return (
    <div className="model-predictions">
      <div className="predictions-header">
        <h3>🤖 ML Model Predictions</h3>
        <div className="predictions-subtitle">
          Advanced forecasting using SVR and ARIMA models
        </div>
      </div>
      
      <div className="predictions-content">
        <div className="prediction-models">
          <div className="prediction-card">
            <div className="prediction-header">
              <div className="model-icon">📊</div>
              <div className="model-info">
                <div className="model-name">SVR Model</div>
                <div className="model-description">Support Vector Regression</div>
              </div>
            </div>
            <div className="prediction-value">
              {svr_prediction ? `${Math.round(svr_prediction)} kW` : 'N/A'}
            </div>
          </div>

          <div className="prediction-card">
            <div className="prediction-header">
              <div className="model-icon">📈</div>
              <div className="model-info">
                <div className="model-name">ARIMA Model</div>
                <div className="model-description">Time Series Analysis</div>
              </div>
            </div>
            <div className="prediction-value">
              {arima_prediction ? `${Math.round(arima_prediction)} kW` : 'N/A'}
            </div>
          </div>

          <div className="prediction-card ensemble">
            <div className="prediction-header">
              <div className="model-icon">🎯</div>
              <div className="model-info">
                <div className="model-name">Ensemble</div>
                <div className="model-description">Combined Prediction</div>
              </div>
            </div>
            <div className="prediction-value">
              {ensemble_prediction ? `${Math.round(ensemble_prediction)} kW` : 'N/A'}
            </div>
          </div>
        </div>

        <div className="prediction-summary">
          <div className="summary-card">
            <div className="summary-header">
              <span className="summary-icon">📊</span>
              <span className="summary-title">Prediction Summary</span>
            </div>
            <div className="summary-content">
              <div className="summary-stat">
                <div className="stat-label">Confidence Level</div>
                <div className="stat-value">{(confidence * 100).toFixed(1)}%</div>
              </div>
              <div className="summary-stat">
                <div className="stat-label">Next Hour Forecast</div>
                <div className="stat-value">
                  {ensemble_prediction ? `${Math.round(ensemble_prediction)} kW` : 'Calculating...'}
                </div>
              </div>
              <div className="summary-stat">
                <div className="stat-label">Trend</div>
                <div className="stat-value">
                  {ensemble_prediction > svr_prediction ? '📈 Rising' : '📉 Stable'}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ModelPredictions;
