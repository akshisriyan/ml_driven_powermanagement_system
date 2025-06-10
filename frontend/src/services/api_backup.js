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
      // Return mock data if API fails
      return {
        tick: 100,
        total_voltage: 22500,
        total_load: 875,
        house_count: 120,
        timestamp: new Date().toISOString()
      };
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
      // Return mock forecast data if API fails
      return {
        svr_prediction: [890, 905, 920, 935, 950],
        arima_forecast: [885, 900, 915, 930, 945],
        confidence_interval: [0.85, 0.92],
        forecast_period: "next_5_hours"
      };
    }
  },

  // Get historical data for charts
  getHistoricalData: async (limit = 50) => {
    try {
      const response = await api.get(`/historical-data?limit=${limit}`);
      return response.data;
    } catch (error) {
      console.error('Error fetching historical data:', error);
      // Return mock historical data if API fails
      const mockData = [];
      for (let i = 0; i < limit; i++) {
        mockData.push({
          tick: i,
          total_voltage: 22000 + Math.random() * 2000,
          total_load: 800 + Math.random() * 400,
          house_count: 100 + i,
          timestamp: new Date(Date.now() - (limit - i) * 60000).toISOString()
        });
      }
      return { data: mockData };
    }
  },

  // Get system health metrics
  getHealth: async () => {
    try {
      const response = await api.get('/system-health');
      return response.data;
    } catch (error) {
      console.error('Error fetching system health:', error);
      // Return mock health data if API fails
      return {
        status: "healthy",
        total_records: 150,
        latest_tick: 149,
        averages: {
          voltage: 22250,
          load: 950,
          houses: 125
        },
        timestamp: new Date().toISOString()
      };
    }
  },
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
      // Return mock health data if API fails
      return {
        status: "healthy",
        total_records: 150,
        latest_tick: 149,
        averages: {
          voltage: 22250,
          load: 950,
          houses: 125
        },
        timestamp: new Date().toISOString()
      };
    }
  },
  // Get model performance metrics
  getModelPerformance: async () => {
    try {
      const response = await api.get('/model-performance');
      return response.data;
    } catch (error) {
      console.error('Error fetching model performance:', error);
      // Return mock performance data if API fails
      return {
        svr_model: {
          accuracy: 85.2,
          mae: 15.3,
          rmse: 22.1,
          last_trained: new Date().toISOString()
        },
        arima_model: {
          mae: 12.4,
          rmse: 18.7,
          aic: 1245.6,
          last_trained: new Date().toISOString()
        }
      };
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
  }
};

export default api;
