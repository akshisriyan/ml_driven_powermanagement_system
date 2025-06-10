import React, { useState, useEffect, useCallback } from 'react';
import { LogOut, User } from 'lucide-react';
import ErrorBoundary from './ErrorBoundary';
import { LoadingScreen } from './Loading';
import Header from './Header';
import GridStatus from './GridStatus';
import Charts from './Charts';
import SimulationControls from './SimulationControls';
import ModelPredictions from './ModelPredictions';
import SystemHealth from './SystemHealth';
import { gridService } from '../services/api';

const Dashboard = ({ onLogout }) => {
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
      console.log('Grid data fetched:', data); // Debug log
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
      console.error('Error fetching forecast data:', error);
    }
  }, []);

  // Fetch historical data
  const fetchHistoricalData = useCallback(async () => {
    try {
      const data = await gridService.getHistoricalData();
      setHistoricalData(data);
    } catch (error) {
      console.error('Error fetching historical data:', error);
    }
  }, []);
  // Fetch health data
  const fetchHealthData = useCallback(async () => {
    try {
      console.log('Fetching health data...');
      const data = await gridService.getHealth();
      console.log('Health data received:', data);
      setHealthData(data);
    } catch (error) {
      console.error('Error fetching health data:', error);
    }
  }, []);

  // Initial data fetch
  const fetchAllData = useCallback(async () => {
    setIsRefreshing(true);
    try {
      await Promise.all([
        fetchGridStatus(),
        fetchForecastData(),
        fetchHistoricalData(),
        fetchHealthData()
      ]);
      setLastUpdated(new Date());
    } catch (error) {
      console.error('Error fetching data:', error);
    } finally {
      setLoading(false);
      setIsRefreshing(false);
    }
  }, [fetchGridStatus, fetchForecastData, fetchHistoricalData, fetchHealthData]);

  // Auto-refresh data
  useEffect(() => {
    fetchAllData();
    
    const interval = setInterval(() => {
      fetchAllData();
    }, 30000); // Refresh every 30 seconds

    return () => clearInterval(interval);
  }, [fetchAllData]);

  // Manual refresh
  const handleRefresh = () => {
    fetchAllData();
  };

  // Simulation handler
  const handleRunSimulation = async (params) => {
    try {
      await gridService.runSimulation(params);
      // Refresh data after simulation
      setTimeout(() => {
        fetchAllData();
      }, 2000);
    } catch (error) {
      console.error('Error running simulation:', error);
    }
  };

  if (loading) {
    return <LoadingScreen />;
  }
  return (
    <ErrorBoundary>
      <div className="dashboard-container">
        {/* Top Navigation Bar */}
        <div className="dashboard-nav">
          <div className="nav-content">
            <div className="nav-left">
              <div className="nav-logo">
                <span className="logo-text">PG</span>
              </div>
              <div className="nav-info">
                <h1 className="nav-title">Power Grid Dashboard</h1>
                <p className="nav-subtitle">ML-Driven Management System</p>
              </div>
            </div>
            
            <div className="nav-right">
              <div className="user-info">
                <User className="user-icon" />
                <span className="user-name">Admin</span>
              </div>
              <button
                onClick={onLogout}
                className="logout-button"
                title="Logout"
              >
                <LogOut className="logout-icon" />
                <span className="logout-text">Logout</span>
              </button>
            </div>
          </div>
        </div>

        {/* Dashboard Header */}
        <div className="dashboard-header-section">
          <Header 
            data={gridData} 
            lastUpdated={lastUpdated}
            onRefresh={handleRefresh}
            isRefreshing={isRefreshing}
          />
        </div>

        {/* Main Dashboard Content */}
        <div className="dashboard-main">
          {error && (
            <div className="error-banner">
              <p>{error}</p>
              <button 
                onClick={handleRefresh}
                className="error-retry"
              >
                Try Again
              </button>
            </div>
          )}          {/* Grid Status Cards */}
          <div className="section">
            <GridStatus gridData={gridData} loading={isRefreshing} />
          </div>

          {/* Charts Section */}
          <div className="section">
            <Charts 
              gridData={gridData}
              historicalData={historicalData}
              forecastData={forecastData}
            />
          </div>

          {/* Control Panels */}
          <div className="controls-section">
            <SimulationControls onRunSimulation={handleRunSimulation} />
            <ModelPredictions data={forecastData} />
          </div>          {/* System Health */}
          <div className="section">
            <SystemHealth healthData={healthData} />
          </div>
        </div>

        {/* Footer */}
        <footer className="dashboard-footer">
          <div className="footer-content">
            <p className="footer-text">
              © 2025 ML-Driven Power Management System - NSBM Computer Science
            </p>
            <div className="footer-dots">
              <div className="dot dot-1"></div>
              <div className="dot dot-2"></div>
              <div className="dot dot-3"></div>
            </div>
          </div>
        </footer>
      </div>
    </ErrorBoundary>
  );
};

export default Dashboard;
