import React from 'react';
import { Brain, TrendingUp, Cpu } from 'lucide-react';

const ModelCard = ({ title, description, prediction, confidence, type, icon: Icon }) => {
  const getTypeColor = () => {
    switch (type) {
      case 'svr': return 'border-blue-400/30 bg-blue-500/10';
      case 'arima': return 'border-purple-400/30 bg-purple-500/10';
      default: return 'border-blue-300/30 bg-blue-400/10';
    }
  };

  const getIconColor = () => {
    switch (type) {
      case 'svr': return 'text-blue-400';
      case 'arima': return 'text-purple-400';
      default: return 'text-blue-300';
    }
  };

  return (
    <div className={`metric-card border-2 ${getTypeColor()} transition-all duration-200 hover:shadow-lg hover:shadow-blue-500/20`}>
      <div className="flex items-start space-x-4">
        <Icon className={`w-8 h-8 ${getIconColor()} mt-1`} />
        <div className="flex-1">
          <h4 className="text-lg font-semibold text-white mb-2 bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">{title}</h4>
          <p className="text-sm text-gray-300 mb-4">{description}</p>
          
          {prediction !== null && prediction !== undefined && (
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium text-gray-300">Prediction:</span>
                <span className="text-lg font-bold text-blue-300">
                  {typeof prediction === 'number' ? prediction.toFixed(2) : prediction} kW
                </span>
              </div>
              
              {confidence && (
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium text-gray-300">Confidence:</span>
                  <span className="text-sm font-medium text-blue-300">{confidence}%</span>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

const ModelPredictions = ({ forecastData, loading }) => {
  if (loading) {
    return (
      <div className="metric-card">
        <div className="flex items-center space-x-2 mb-6">
          <Brain className="w-5 h-5 text-blue-400" />
          <h3 className="text-lg font-semibold text-white bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">ML Model Predictions</h3>
        </div>
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {[...Array(2)].map((_, i) => (
            <div key={i} className="metric-card border-2 border-blue-300/30 animate-pulse">
              <div className="flex items-start space-x-4">
                <div className="w-8 h-8 bg-blue-300/30 rounded"></div>
                <div className="flex-1">
                  <div className="h-6 bg-blue-300/30 rounded w-32 mb-2"></div>
                  <div className="h-4 bg-blue-300/30 rounded w-full mb-4"></div>
                  <div className="space-y-2">
                    <div className="h-4 bg-blue-300/30 rounded w-24"></div>
                    <div className="h-4 bg-blue-300/30 rounded w-20"></div>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  const svrPrediction = forecastData?.svr_prediction;
  const arimaForecast = forecastData?.arima_forecast;
  const nextStepArima = arimaForecast && arimaForecast.length > 0 ? arimaForecast[0] : null;

  return (
    <div className="metric-card">
      <div className="flex items-center space-x-2 mb-6">
        <Brain className="w-5 h-5 text-blue-400" />
        <h3 className="text-lg font-semibold text-white bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">ML Model Predictions</h3>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <ModelCard
          title="SVR Model"
          description="Support Vector Regression for load prediction based on voltage and house count patterns"
          prediction={svrPrediction}
          confidence={85}
          type="svr"
          icon={Cpu}
        />

        <ModelCard
          title="ARIMA Model"
          description="Time series forecasting model for predicting future load trends"
          prediction={nextStepArima}
          confidence={78}
          type="arima"
          icon={TrendingUp}
        />
      </div>

      {/* Model Performance Summary */}
      <div className="mt-6 metric-card">
        <h4 className="text-sm font-medium text-white mb-3 bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">Model Performance Summary</h4>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs">
          <div className="flex justify-between">
            <span className="text-gray-300">SVR Accuracy:</span>
            <span className="font-medium text-blue-300">85.2%</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-300">ARIMA MAE:</span>
            <span className="font-medium text-blue-300">12.4 kW</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-300">Last Updated:</span>
            <span className="font-medium text-blue-300">Just now</span>
          </div>
        </div>
      </div>

      {/* Forecast Timeline */}
      {arimaForecast && arimaForecast.length > 1 && (
        <div className="mt-6">
          <h4 className="text-sm font-medium text-white mb-3 bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">ARIMA 10-Step Forecast</h4>
          <div className="grid grid-cols-5 gap-2">
            {arimaForecast.slice(0, 10).map((value, index) => (
              <div key={index} className="text-center p-2 bg-blue-500/20 rounded border border-blue-400/30 backdrop-blur-sm">
                <div className="text-xs text-blue-300 font-medium">Step {index + 1}</div>
                <div className="text-sm font-bold text-blue-200">
                  {value?.toFixed(1)} kW
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default ModelPredictions;
