import axios from 'axios';

const API_BASE_URL = 'http://localhost:5000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: { 'Content-Type': 'application/json' },
});

// Attach token automatically
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const authService = {
  login: async ({ username, password }) => {
    const form = new URLSearchParams();
    form.append('username', username);
    form.append('password', password);
    const { data } = await api.post('/auth/token', form, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    });
    return data;
  },
  register: async ({ username, email, password, role }) => {
    const { data } = await api.post('/auth/register', { username, email, password, role });
    return data;
  },
  me: async () => {
    const { data } = await api.get('/auth/me');
    return data;
  }
};

export const gridService = {
  // Get current grid status
  getGridStatus: async () => {
    try {
      const response = await api.get('/api/grid/grid-status');
      return response.data;
    } catch (error) {
      console.error('Error fetching grid status:', error);
      // Return mock data if API fails - using realistic voltage range
      return {
        tick: 100,
        total_voltage: 220,
        total_load: 875,
        timestamp: new Date().toISOString()
      };
    }
  },

  // Run simulation with parameters
  runSimulation: async (params) => {
    try {
      const response = await api.post('/api/grid/simulate', params);
      return response.data;
    } catch (error) {
      console.error('Error running simulation:', error);
      throw error;
    }
  },

  // Get forecast data
  getForecast: async () => {
    try {
      const response = await api.get('/api/grid/forecast');
      return response.data;
    } catch (error) {
      console.error('Error fetching forecast:', error);
      // Return mock forecast data if API fails
      return {
        svr_prediction: 900,
        arima_prediction: 895,
        ensemble_prediction: 897.5,
        confidence: 0.8,
        // compatibility for any components using a horizon
        arima_forecast: [885, 900, 915, 930, 945],
        forecast_period: "next_5_hours"
      };
    }
  },

  // Get historical data for charts
  getHistoricalData: async (limit = 50) => {
    try {
      const response = await api.get(`/api/grid/historical-data?limit=${limit}`);
      return response.data;
    } catch (error) {
      console.error('Error fetching historical data:', error);
      // Return mock historical data if API fails
      const mockData = [];
      for (let i = 0; i < limit; i++) {
        mockData.push({
          tick: i,
          total_voltage: 220 + Math.random() * 20,  // Use realistic 220V range
          total_load: 800 + Math.random() * 400,
          timestamp: new Date(Date.now() - (limit - i) * 60000).toISOString()
        });
      }
      return mockData;
    }
  },

  // Get system health metrics
  getHealth: async () => {
    try {
      const response = await api.get('/api/grid/system-health');
      return response.data;
    } catch (error) {
      console.error('Error fetching system health:', error);
      // Return mock health data if API fails
      return {
        status: "healthy",
        total_records: 150,
        latest_tick: 149,
        averages: {
          voltage: 220,  // Updated to realistic voltage range
          load: 950
        },
        timestamp: new Date().toISOString()
      };
    }
  },

  // Get system health metrics (alias for compatibility)
  getSystemHealth: async () => {
    return gridService.getHealth();
  },

  // Get model performance metrics
  getModelPerformance: async () => {
    try {
      const response = await api.get('/api/grid/model-performance');
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
  },

  // Get voltage forecast (ARIMA-based)
  getVoltageForecast: async () => {
    try {
      const response = await api.get('/api/grid/voltage-forecast');
      return response.data;
    } catch (error) {
      console.error('Error fetching voltage forecast:', error);
      // Return mock forecast data if API fails - using realistic 220V range
      return {
        current_voltage: 220,
        forecast_timestamp: new Date().toISOString(),
        model_info: {
          aic: 850.5,
          order: [1, 1, 1],
          model_type: 'SARIMAX',
          environmental_factors: 5
        },
        environmental_impact: {
          temperature_effect: 'normal',
          solar_contribution: 'medium',
          wind_contribution: 'medium'
        },
        current_conditions: {
          temperature: 25.0,
          humidity: 50.0,
          solar_intensity: 500.0,
          wind_speed: 5.0,
          peak_hours: 0.0
        },
        hourly_forecast: {
          data: Array.from({ length: 60 }, (_, i) => ({
            time: new Date(Date.now() + (i + 1) * 60000).toISOString(),
            voltage: 220 + Math.random() * 20 - 10,
            confidence_lower: 210 + Math.random() * 20 - 10,
            confidence_upper: 230 + Math.random() * 20 - 10
          })),
          average: 220,
          trend: 'stable',
          change_percent: 0.0,
          min_voltage: 215,
          max_voltage: 225
        },
        daily_forecast: {
          data: Array.from({ length: 24 }, (_, i) => ({
            time: new Date(Date.now() + (i + 1) * 3600000).toISOString(),
            voltage: 220 + Math.random() * 30 - 15,
            confidence_lower: 200 + Math.random() * 30 - 15,
            confidence_upper: 240 + Math.random() * 30 - 15
          })),
          average: 220,
          trend: 'stable',
          change_percent: 0.0,
          min_voltage: 210,
          max_voltage: 230
        }
      };
    }
  },

  // Get forecast summary
  getForecastSummary: async () => {
    try {
      const response = await api.get('/api/grid/forecast-summary');
      return response.data;
    } catch (error) {
      console.error('Error fetching forecast summary:', error);
      // Return mock summary data if API fails - using realistic voltage range
      return {
        current_voltage: 220,
        forecast_timestamp: new Date().toISOString(),
        predictions: {
          next_hour: {
            average_voltage: 218,
            change_percentage: -0.9,
            trend: 'decreasing'
          },
          next_day: {
            average_voltage: 215,
            change_percentage: -2.3,
            trend: 'decreasing'
          }
        },
        alerts: [
          {
            type: 'info',
            message: 'Slight voltage decrease expected over next 24 hours',
            severity: 'low'
          }
        ],
        confidence: 'high'
      };
    }
  },

  // Upload Excel file
  uploadExcel: async (file) => {
    try {
      const formData = new FormData();
      formData.append('file', file);
      
      const response = await api.post('/api/grid/upload-excel', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      return response.data;
    } catch (error) {
      console.error('Error uploading Excel file:', error);
      throw error;
    }
  },

  // Export data as CSV
  exportData: async () => {
    try {
      const response = await api.get('/api/grid/export-data', {
        responseType: 'blob',
      });
      
      // Create blob URL and trigger download
      const blob = new Blob([response.data], { type: 'text/csv' });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `power_grid_export_${new Date().toISOString().split('T')[0]}.csv`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
      
      return { success: true, message: 'Data exported successfully' };
    } catch (error) {
      console.error('Error exporting data:', error);
      throw error;
    }
  },

  // Get data statistics
  getDataStatistics: async () => {
    try {
      const response = await api.get('/api/grid/data-statistics');
      return response.data;
    } catch (error) {
      console.error('Error fetching data statistics:', error);
      // Return mock data if API fails
      return {
        total_records: 0,
        oldest_record: null,
        newest_record: null,
        avg_voltage: 0,
        avg_load: 0,
        avg_houses: 0,
        estimated_size: "0 KB"
      };
    }
  },
};

// University Billing services
export const billingService = {
  uploadExcel: async (file) => {
    const formData = new FormData();
    formData.append('file', file);
    const { data } = await api.post('/billing/upload-excel', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return data;
  },
  getSummary: async () => {
    const { data } = await api.get('/billing/summary');
    return data;
  },
  getMonthly: async () => {
    const { data } = await api.get('/billing/monthly');
    return data;
  }
};

export const controlService = {
  getGenerator: async () => {
    const { data } = await api.get('/control/generator');
    return data;
  },
  setGenerator: async (enabled) => {
    const { data } = await api.post('/control/generator', { enabled });
    return data;
  }
};

export const zonesService = {
  list: async () => {
    const { data } = await api.get('/api/zones');
    return data;
  },
  summary: async () => {
    const { data } = await api.get('/api/zones/summary');
    return data;
  }
};

export default api;
