
import React, { useState, useEffect, useCallback } from 'react';
import { Routes, Route, Navigate, useLocation } from 'react-router-dom';
import ErrorBoundary from './components/ErrorBoundary';
import { LoadingScreen } from './components/Loading';
import Header from './components/Header';
import TopNotification from './components/TopNotification';
import GridStatus from './components/GridStatus';
import Charts from './components/Charts';
import SimulationControls from './components/SimulationControls';
import ModelPredictions from './components/ModelPredictions';
import SystemHealth from './components/SystemHealth';
import VoltageForecast from './components/VoltageForecast';
import DataManager from './components/DataManager';
import Billing from './components/Billing';
import Zones from './components/Zones';
import Navbar from './components/Navbar';
import Footer from './components/Footer';
import Login from './components/Login';
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
  const [user, setUser] = useState(() => {
    try { return JSON.parse(localStorage.getItem('user') || 'null'); } catch { return null; }
  });
  const location = useLocation();

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

  // Load data on component mount if authenticated
  useEffect(() => {
    if (user) {
      loadData();
    }
  }, [loadData, user]);

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
  if (!user) {
    return (
      <ErrorBoundary>
        <Login onAuth={(u) => setUser(u)} />
      </ErrorBoundary>
    );
  }

  const isAdmin = user.role === 'admin';

  return (
    <ErrorBoundary>
      {loading && <LoadingScreen message="Loading data..." />}
      <div className="App">
        <TopNotification />
        <Navbar user={user} onLogout={() => { localStorage.clear(); setUser(null); }} currentPath={location.pathname} />
        <div className="dashboard-content">
          <Routes>
            {/* Summary Dashboard */}
            <Route path="/" element={
              <>
                <div className="dashboard-header">
                  <h1>⚡ ML-Driven Power Grid Management</h1>
                  <p>Real-time monitoring and intelligent power distribution</p>
                </div>
                <Header onRefresh={refreshData} lastUpdated={lastUpdated} isRefreshing={isRefreshing} />
                {error && (
                  <div className="error fade-in-up">
                    <div style={{display: 'flex', alignItems: 'center', gap: '8px'}}>
                      <span>⚠️</span>
                      <span>{error}</span>
                    </div>
                  </div>
                )}
                <GridStatus gridData={gridData} loading={isRefreshing} />
              </>
            }/>

            {/* Analytics page: Charts, Forecast, Predictions */}
            <Route path="/analytics" element={
              <>
                <Charts gridData={gridData} forecastData={forecastData} historicalData={historicalData} loading={isRefreshing} />
                <VoltageForecast loading={isRefreshing} />
                <ModelPredictions forecastData={forecastData} loading={isRefreshing} />
              </>
            }/>

            {/* Data manager - admin only */}
            <Route path="/data" element={isAdmin ? <DataManager loading={isRefreshing} /> : <Navigate to="/" replace />} />

            {/* Models page - admin only: run simulation and models area */}
            <Route path="/models" element={isAdmin ? (
              <>
                <SimulationControls onRunSimulation={runSimulation} loading={isRefreshing} />
                <ModelPredictions forecastData={forecastData} loading={isRefreshing} />
              </>
            ) : <Navigate to="/" replace />} />

            {/* Health page */}
            <Route path="/health" element={<SystemHealth healthData={healthData} loading={isRefreshing} />} />

            {/* Billing page */}
            <Route path="/billing" element={<Billing />} />

            {/* Zones page */}
            <Route path="/zones" element={<Zones />} />

            {/* Fallback */}
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </div>
        <Footer />
      </div>
    </ErrorBoundary>
  );
}

export default App;
