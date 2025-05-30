import React, { useState } from 'react';
import { Play, Settings, RefreshCw, AlertCircle } from 'lucide-react';

const SimulationControls = ({ onRunSimulation, loading }) => {
  const [houseGrowthRate, setHouseGrowthRate] = useState(0.02);
  const [isRunning, setIsRunning] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);

  const handleRunSimulation = async () => {
    setIsRunning(true);
    setError(null);
    setSuccess(false);

    try {
      await onRunSimulation({ house_growth_rate: houseGrowthRate });
      setSuccess(true);
      setTimeout(() => setSuccess(false), 3000);
    } catch (err) {
      setError(err.message || 'Failed to run simulation');
      setTimeout(() => setError(null), 5000);
    } finally {
      setIsRunning(false);
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
      <div className="flex items-center space-x-2 mb-6">
        <Settings className="w-5 h-5 text-primary-600" />
        <h3 className="text-lg font-semibold text-gray-800">Simulation Controls</h3>
      </div>

      <div className="space-y-6">
        {/* Parameter Controls */}
        <div>
          <label htmlFor="growth-rate" className="block text-sm font-medium text-gray-700 mb-2">
            House Growth Rate
          </label>
          <div className="flex items-center space-x-4">
            <input
              id="growth-rate"
              type="range"
              min="0.001"
              max="0.1"
              step="0.001"
              value={houseGrowthRate}
              onChange={(e) => setHouseGrowthRate(parseFloat(e.target.value))}
              className="flex-1 h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
            />
            <span className="text-sm font-medium text-gray-600 min-w-[60px]">
              {(houseGrowthRate * 100).toFixed(1)}%
            </span>
          </div>
          <p className="text-xs text-gray-500 mt-1">
            Controls how fast new houses are added to the grid
          </p>
        </div>

        {/* Run Button */}
        <div className="flex flex-col space-y-3">
          <button
            onClick={handleRunSimulation}
            disabled={isRunning || loading}
            className={`
              flex items-center justify-center space-x-2 px-6 py-3 rounded-lg font-medium transition-all duration-200
              ${isRunning || loading
                ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                : 'bg-primary-600 hover:bg-primary-700 text-white shadow-sm hover:shadow'
              }
            `}
          >
            {isRunning ? (
              <>
                <RefreshCw className="w-4 h-4 animate-spin" />
                <span>Running Simulation...</span>
              </>
            ) : (
              <>
                <Play className="w-4 h-4" />
                <span>Run Simulation</span>
              </>
            )}
          </button>

          {/* Status Messages */}
          {error && (
            <div className="flex items-center space-x-2 p-3 bg-danger-50 border border-danger-200 rounded-lg">
              <AlertCircle className="w-4 h-4 text-danger-600" />
              <span className="text-sm text-danger-700">{error}</span>
            </div>
          )}

          {success && (
            <div className="flex items-center space-x-2 p-3 bg-success-50 border border-success-200 rounded-lg">
              <div className="w-4 h-4 text-success-600">✓</div>
              <span className="text-sm text-success-700">Simulation completed successfully!</span>
            </div>
          )}
        </div>

        {/* Simulation Info */}
        <div className="bg-gray-50 rounded-lg p-4">
          <h4 className="text-sm font-medium text-gray-800 mb-2">Simulation Parameters</h4>
          <div className="space-y-1 text-xs text-gray-600">
            <div className="flex justify-between">
              <span>Growth Rate:</span>
              <span>{(houseGrowthRate * 100).toFixed(3)}%</span>
            </div>
            <div className="flex justify-between">
              <span>Model:</span>
              <span>NetLogo Power Grid</span>
            </div>
            <div className="flex justify-between">
              <span>Output:</span>
              <span>CSV Data Export</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SimulationControls;
