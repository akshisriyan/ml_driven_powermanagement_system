import React, { useState } from 'react';
import './SimulationControls.css';

const SimulationControls = ({ onRunSimulation, loading }) => {
  const [isRunning, setIsRunning] = useState(false);
  const [simulationParams, setSimulationParams] = useState({
    steps: 100,
    houses: 120,
    voltage: 22500,
    house_growth_rate: 0.05, // 5% default growth rate (decimal)
    temperature: 25.0,      // Default temperature in °C
    humidity: 50.0,        // Default humidity in %
    solar_intensity: 500.0, // Default solar intensity
    wind_speed: 5.0,       // Default wind speed in m/s
    peak_hours: false      // Default not peak hours
  });

  const handleRunSimulation = async () => {
    if (isRunning || loading) return;
    
    setIsRunning(true);
    try {
      // Send all simulation parameters including environmental ones
      await onRunSimulation({
        house_growth_rate: Number(simulationParams.house_growth_rate) || 0,
        temperature: Number(simulationParams.temperature) || 25.0,
        humidity: Number(simulationParams.humidity) || 50.0,
        solar_intensity: Number(simulationParams.solar_intensity) || 500.0,
        wind_speed: Number(simulationParams.wind_speed) || 5.0,
        peak_hours: Boolean(simulationParams.peak_hours),
        steps: Number(simulationParams.steps),
        houses: Number(simulationParams.houses),
        voltage: Number(simulationParams.voltage)
      });
    } catch (error) {
      console.error('Simulation failed:', error);
    } finally {
      setIsRunning(false);
    }
  };

  const handleParamChange = (param, value) => {
    setSimulationParams(prev => ({
      ...prev,
      [param]: param === 'peak_hours' 
        ? Boolean(value)
        : param === 'house_growth_rate' || param === 'temperature' || param === 'humidity' || param === 'wind_speed'
          ? (parseFloat(value) || 0)
          : (parseInt(value) || 0)
    }));
  };

  return (
    <div className="simulation-controls">
      <div className="controls-header">
        <h3>🎮 Simulation Controls</h3>
      </div>
      
      <div className="controls-content">
        <div className="param-group">
          <label className="param-label">
            Simulation Steps:
            <input
              type="number"
              value={simulationParams.steps}
              onChange={(e) => handleParamChange('steps', e.target.value)}
              min="10"
              max="1000"
              className="param-input"
            />
          </label>
        </div>

        <div className="param-group">
          <label className="param-label">
            Number of Campus Units:
            <input
              type="number"
              value={simulationParams.houses}
              onChange={(e) => handleParamChange('houses', e.target.value)}
              min="50"
              max="200"
              className="param-input"
            />
          </label>
        </div>

        <div className="param-group">
          <label className="param-label">
            Initial Voltage:
            <input
              type="number"
              value={simulationParams.voltage}
              onChange={(e) => handleParamChange('voltage', e.target.value)}
              min="20000"
              max="25000"
              className="param-input"
            />
          </label>
        </div>

        <div className="param-group">
          <label className="param-label">
            Unit Growth Rate (decimal):
            <input
              type="number"
              step="0.01"
              value={simulationParams.house_growth_rate}
              onChange={(e) => handleParamChange('house_growth_rate', e.target.value)}
              min="0"
              max="1"
              className="param-input"
            />
          </label>
        </div>

        <div className="param-group">
          <label className="param-label">
            Temperature (°C):
            <input
              type="number"
              step="0.1"
              value={simulationParams.temperature}
              onChange={(e) => handleParamChange('temperature', e.target.value)}
              min="0"
              max="50"
              className="param-input"
            />
          </label>
        </div>

        <div className="param-group">
          <label className="param-label">
            Humidity (%):
            <input
              type="number"
              step="0.1"
              value={simulationParams.humidity}
              onChange={(e) => handleParamChange('humidity', e.target.value)}
              min="0"
              max="100"
              className="param-input"
            />
          </label>
        </div>

        <div className="param-group">
          <label className="param-label">
            Solar Intensity:
            <input
              type="number"
              step="1"
              value={simulationParams.solar_intensity}
              onChange={(e) => handleParamChange('solar_intensity', e.target.value)}
              min="0"
              max="1000"
              className="param-input"
            />
          </label>
        </div>

        <div className="param-group">
          <label className="param-label">
            Wind Speed (m/s):
            <input
              type="number"
              step="0.1"
              value={simulationParams.wind_speed}
              onChange={(e) => handleParamChange('wind_speed', e.target.value)}
              min="0"
              max="30"
              className="param-input"
            />
          </label>
        </div>

        <div className="param-group">
          <label className="param-label">
            Peak Hours:
            <input
              type="checkbox"
              checked={simulationParams.peak_hours}
              onChange={(e) => handleParamChange('peak_hours', e.target.checked)}
              className="param-checkbox"
            />
          </label>
        </div>

        <button
          className={`run-simulation-btn ${isRunning || loading ? 'running' : ''}`}
          onClick={handleRunSimulation}
          disabled={isRunning || loading}
        >
          <span className="btn-icon">
            {isRunning || loading ? '⏳' : '▶️'}
          </span>
          {isRunning || loading ? 'Running...' : 'Run Simulation'}
        </button>

        <div className="simulation-status">
          {isRunning && (
            <div className="status-message">
              <span className="status-icon">🔄</span>
              <span>Simulation in progress...</span>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default SimulationControls;
