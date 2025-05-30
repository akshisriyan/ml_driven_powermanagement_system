import React from 'react';
import {
  LineChart,
  Line,
  AreaChart,
  Area,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
} from 'recharts';

const ChartContainer = ({ title, children, className = "" }) => (
  <div className={`bg-white rounded-lg shadow-sm border border-gray-200 p-6 ${className}`}>
    <h3 className="text-lg font-semibold text-gray-800 mb-4">{title}</h3>
    <div className="h-80">
      {children}
    </div>
  </div>
);

const Charts = ({ gridData, forecastData, historicalData }) => {
  // Generate sample historical data for demo purposes if no real data available
  const generateHistoricalData = () => {
    const data = [];
    for (let i = 30; i >= 0; i--) {
      data.push({
        tick: (gridData?.tick || 100) - i,
        voltage: (gridData?.total_voltage || 24000) + (Math.random() - 0.5) * 2000,
        load: (gridData?.total_load || 1000) + (Math.random() - 0.5) * 200,
        houses: (gridData?.house_count || 100) + Math.floor((Math.random() - 0.5) * 10),
      });
    }
    return data;
  };

  // Use real historical data if available, otherwise use generated data
  const histData = historicalData?.data?.length > 0 
    ? historicalData.data.map(item => ({
        tick: item.tick,
        voltage: item.total_voltage,
        load: item.total_load,
        houses: item.house_count,
      }))
    : generateHistoricalData();

  // Voltage trend chart
  const VoltageChart = () => (
    <ChartContainer title="Voltage Trend Over Time">
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart data={histData}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="tick" />
          <YAxis />
          <Tooltip formatter={(value) => [`${value.toFixed(1)} V`, 'Voltage']} />
          <Area 
            type="monotone" 
            dataKey="voltage" 
            stroke="#3b82f6" 
            fill="#3b82f6" 
            fillOpacity={0.3}
          />
        </AreaChart>
      </ResponsiveContainer>
    </ChartContainer>
  );

  // Load and House Count chart
  const LoadHouseChart = () => (
    <ChartContainer title="Load vs House Count">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={histData}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="tick" />
          <YAxis yAxisId="left" />
          <YAxis yAxisId="right" orientation="right" />
          <Tooltip />
          <Legend />
          <Line 
            yAxisId="left"
            type="monotone" 
            dataKey="load" 
            stroke="#ef4444" 
            strokeWidth={2}
            name="Load (kW)"
          />
          <Line 
            yAxisId="right"
            type="monotone" 
            dataKey="houses" 
            stroke="#22c55e" 
            strokeWidth={2}
            name="House Count"
          />
        </LineChart>
      </ResponsiveContainer>
    </ChartContainer>
  );

  // Forecast chart
  const ForecastChart = () => {
    const forecastChartData = forecastData?.arima_forecast?.map((value, index) => ({
      step: index + 1,
      forecast: value,
      current: index === 0 ? (gridData?.total_load || 1000) : null,
    })) || [];

    return (
      <ChartContainer title="ARIMA Load Forecast (Next 10 Steps)">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={forecastChartData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="step" />
            <YAxis />
            <Tooltip formatter={(value) => [`${value?.toFixed(1)} kW`, 'Predicted Load']} />
            <Bar dataKey="forecast" fill="#f59e0b" />
            {forecastChartData[0]?.current && (
              <Bar dataKey="current" fill="#22c55e" />
            )}
          </BarChart>
        </ResponsiveContainer>
      </ChartContainer>
    );
  };

  // Power distribution pie chart
  const PowerDistributionChart = () => {
    const distributionData = [
      { name: 'Residential', value: 60, color: '#3b82f6' },
      { name: 'Commercial', value: 25, color: '#ef4444' },
      { name: 'Industrial', value: 10, color: '#f59e0b' },
      { name: 'Others', value: 5, color: '#22c55e' },
    ];

    return (
      <ChartContainer title="Power Distribution by Sector">
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie
              data={distributionData}
              cx="50%"
              cy="50%"
              outerRadius={100}
              dataKey="value"
              label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
            >
              {distributionData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={entry.color} />
              ))}
            </Pie>
            <Tooltip formatter={(value) => [`${value}%`, 'Share']} />
          </PieChart>
        </ResponsiveContainer>
      </ChartContainer>
    );
  };

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <VoltageChart />
        <LoadHouseChart />
      </div>
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <ForecastChart />
        <PowerDistributionChart />
      </div>
    </div>
  );
};

export default Charts;
