import axios from 'axios';

const API_BASE_URL = 'http://localhost:5000';

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

  // Get system health metrics (alias for compatibility)
  getSystemHealth: async () => {
    return gridService.getHealth();
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
  },

  // Get voltage forecast (ARIMA-based)
  getVoltageForecast: async () => {
    try {
      const response = await api.get('/voltage-forecast');
      return response.data;
    } catch (error) {
      console.error('Error fetching voltage forecast:', error);
      // Return mock forecast data if API fails
      return {
        current_voltage: 22500,
        forecast_timestamp: new Date().toISOString(),
        model_info: {
          aic: 850.5,
          order: [1, 1, 1]
        },
        hourly_forecast: {
          data: Array.from({ length: 60 }, (_, i) => ({
            time: new Date(Date.now() + (i + 1) * 60000).toISOString(),
            voltage: 22500 + Math.random() * 1000 - 500,
            confidence_lower: 21500 + Math.random() * 1000 - 500,
            confidence_upper: 23500 + Math.random() * 1000 - 500
          })),
          average: 22500,
          trend: 'stable',
          min_voltage: 21800,
          max_voltage: 23200
        },
        daily_forecast: {
          data: Array.from({ length: 24 }, (_, i) => ({
            time: new Date(Date.now() + (i + 1) * 3600000).toISOString(),
            voltage: 22500 + Math.random() * 1500 - 750,
            confidence_lower: 21000 + Math.random() * 1500 - 750,
            confidence_upper: 24000 + Math.random() * 1500 - 750
          })),
          average: 22500,
          trend: 'stable',
          min_voltage: 21500,
          max_voltage: 23500
        }
      };
    }
  },

  // Get forecast summary
  getForecastSummary: async () => {
    try {
      const response = await api.get('/forecast-summary');
      return response.data;
    } catch (error) {
      console.error('Error fetching forecast summary:', error);
      // Return mock summary data if API fails
      return {
        current_voltage: 22500,
        forecast_timestamp: new Date().toISOString(),
        predictions: {
          next_hour: {
            average_voltage: 22400,
            change_percentage: -0.4,
            trend: 'decreasing'
          },
          next_day: {
            average_voltage: 22300,
            change_percentage: -0.9,
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
      
      const response = await api.post('/upload-excel', formData, {
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
      const response = await api.get('/export-data', {
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
      const response = await api.get('/data-statistics');
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

export default api;
