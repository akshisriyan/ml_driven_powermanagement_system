import React, { useState } from 'react';

const SimulationControls = ({ onRunSimulation, loading }) => {
  const [isRunning, setIsRunning] = useState(false);
  const [simulationParams, setSimulationParams] = useState({
    steps: 100,
    houses: 120,
    voltage: 22500
  });

  const handleRunSimulation = async () => {
    if (isRunning || loading) return;
    
    setIsRunning(true);
    try {
      await onRunSimulation(simulationParams);
    } catch (error) {
      console.error('Simulation failed:', error);
    } finally {
      setIsRunning(false);
    }
  };

  const handleParamChange = (param, value) => {
    setSimulationParams(prev => ({
      ...prev,
      [param]: parseInt(value) || 0
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
            Number of Houses:
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
