import React, { useState, useEffect, useCallback } from 'react';
import ErrorBoundary from './components/ErrorBoundary';
import { LoadingScreen } from './components/Loading';
import Header from './components/Header';
import GridStatus from './components/GridStatus';
import Charts from './components/Charts';
import SimulationControls from './components/SimulationControls';
import ModelPredictions from './components/ModelPredictions';
import SystemHealth from './components/SystemHealth';
import { gridService } from './services/api';
import './App.css';

function App() {
  const [gridData, setGridData] = useState({});
  const [forecastData, setForecastData] = useState({});
  const [historicalData, setHistoricalData] = useState({});
  const [healthData, setHealthData] = useState({});
  const [loading, setLoading] = useState(true);
  const [lastUpdated, setLastUpdated] = useState(null);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [error, setError] = useState(null);

  // Fetch grid status
  const fetchGridStatus = useCallback(async () => {
    try {
      const data = await gridService.getGridStatus();
      setGridData(data);
      setError(null);
    } catch (error) {
      console.error('Error fetching grid status:', error);
      setError('Failed to fetch grid status');
    }
  }, []);

  // Fetch forecast data
  const fetchForecastData = useCallback(async () => {
    try {
      const data = await gridService.getForecast();
      setForecastData(data);
    } catch (error) {
      console.error('Error fetching forecast:', error);
      // Don't set error for forecast as it's not critical
    }
  }, []);

  // Fetch historical data
  const fetchHistoricalData = useCallback(async () => {
    try {
      const data = await gridService.getHistoricalData(50);
      setHistoricalData(data);
    } catch (error) {
      console.error('Error fetching historical data:', error);
    }
  }, []);

  // Fetch system health
  const fetchSystemHealth = useCallback(async () => {
    try {
      const data = await gridService.getSystemHealth();
      setHealthData(data);
    } catch (error) {
      console.error('Error fetching system health:', error);
    }
  }, []);

  // Initial data load
  const loadData = useCallback(async () => {
    setLoading(true);
    try {
      await Promise.all([
        fetchGridStatus(),
        fetchForecastData(),
        fetchHistoricalData(),
        fetchSystemHealth(),
      ]);
      setLastUpdated(new Date().toISOString());
    } catch (error) {
      console.error('Error loading data:', error);
    } finally {
      setLoading(false);
    }
  }, [fetchGridStatus, fetchForecastData, fetchHistoricalData, fetchSystemHealth]);

  // Refresh data
  const refreshData = useCallback(async () => {
    setIsRefreshing(true);
    await loadData();
    setIsRefreshing(false);
  }, [loadData]);

  // Run simulation
  const runSimulation = useCallback(async (params) => {
    try {
      await gridService.runSimulation(params);
      // Refresh data after simulation
      setTimeout(() => {
        refreshData();
      }, 2000); // Wait 2 seconds for simulation to complete
    } catch (error) {
      console.error('Error running simulation:', error);
      throw error;
    }
  }, [refreshData]);

  // Load data on component mount
  useEffect(() => {
    loadData();
  }, [loadData]);

  // Auto-refresh every 30 seconds
  useEffect(() => {
    const interval = setInterval(() => {
      if (!isRefreshing && !loading) {
        fetchGridStatus();
        fetchForecastData();
        fetchSystemHealth();
        setLastUpdated(new Date().toISOString());
      }
    }, 30000);

    return () => clearInterval(interval);
  }, [fetchGridStatus, fetchForecastData, fetchSystemHealth, isRefreshing, loading]);
  return (
    <ErrorBoundary>
      {loading ? (
        <LoadingScreen message="Initializing power grid dashboard..." />
      ) : (
        <div className="App">
          <div className="dashboard-content">
            <div className="dashboard-header">
              <h1>⚡ ML-Driven Power Grid Management</h1>
              <p>Real-time monitoring and intelligent power distribution</p>
              <h1>NSBM Green University</h1>
            </div>

            <Header 
              onRefresh={refreshData}
              lastUpdated={lastUpdated}
              isRefreshing={isRefreshing}
            />

            {/* Error Banner */}
            {error && (
              <div className="error fade-in-up">
                <div style={{display: 'flex', alignItems: 'center', gap: '8px'}}>
                  <span>⚠️</span>
                  <span>{error}</span>
                </div>
              </div>
            )}            {/* Grid Status Cards */}
            <GridStatus gridData={gridData} loading={isRefreshing} />

            {/* Main Content Grid */}
            <div className="controls-section">
              {/* Left Column - Charts */}
              <div>
                <Charts 
                  gridData={gridData}
                  forecastData={forecastData}
                  historicalData={historicalData}
                  loading={isRefreshing}
                />
              </div>

              {/* Right Column - Controls and System Health */}
              <div>
                <SimulationControls 
                  onRunSimulation={runSimulation}
                  loading={isRefreshing}
                />
                <SystemHealth 
                  healthData={healthData}
                  loading={isRefreshing}
                />
              </div>
            </div>

            {/* Model Predictions - Full Width */}
            <ModelPredictions 
              forecastData={forecastData}
              loading={isRefreshing}
            />
          </div>
        </div>
      )}
    </ErrorBoundary>
  );
}

export default App;
