import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const gridService = {
  // Get current grid status
  getGridStatus: async () => {
    try {
      const response = await api.get('/grid-status');
      return response.data;
    } catch (error) {
      console.error('Error fetching grid status:', error);
      throw error;
    }
  },

  // Run simulation with parameters
  runSimulation: async (params) => {
    try {
      const response = await api.post('/simulate', params);
      return response.data;
    } catch (error) {
      console.error('Error running simulation:', error);
      throw error;
    }
  },

  // Get forecast data
  getForecast: async () => {
    try {
      const response = await api.get('/forecast');
      return response.data;
    } catch (error) {
      console.error('Error fetching forecast:', error);
      throw error;
    }
  },

  // Get historical data for charts
  getHistoricalData: async (limit = 100) => {
    try {
      const response = await api.get(`/historical-data?limit=${limit}`);
      return response.data;
    } catch (error) {
      console.error('Error fetching historical data:', error);
      throw error;
    }
  },

  // Get system health metrics
  getSystemHealth: async () => {
    try {
      const response = await api.get('/system-health');
      return response.data;
    } catch (error) {
      console.error('Error fetching system health:', error);
      throw error;
    }
  },

  // Get model performance metrics
  getModelPerformance: async () => {
    try {
      const response = await api.get('/model-performance');
      return response.data;
    } catch (error) {
      console.error('Error fetching model performance:', error);
      throw error;
    }
  },

  // Clear all data (for testing)
  clearData: async () => {
    try {
      const response = await api.delete('/clear-data');
      return response.data;
    } catch (error) {
      console.error('Error clearing data:', error);
      throw error;
    }
  },
};

export default api;
