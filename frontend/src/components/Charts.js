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
  <div className={`metric-card ${className}`}>
    <h3 className="text-lg font-semibold text-white mb-4 bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">{title}</h3>
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
          <Tooltip formatter={(value) => [`${value.toFixed(1)} V`, 'Voltage']} 
            contentStyle={{
              backgroundColor: 'rgba(255, 255, 255, 0.95)',
              border: '1px solid #667eea',
              borderRadius: '8px',
              boxShadow: '0 4px 6px rgba(102, 126, 234, 0.2)'
            }}
          />          <Area 
            type="monotone" 
            dataKey="voltage" 
            stroke="#667eea" 
            fill="url(#voltageGradient)" 
            fillOpacity={0.8}
          />
          <defs>
            <linearGradient id="voltageGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#667eea" stopOpacity={0.8}/>
              <stop offset="95%" stopColor="#764ba2" stopOpacity={0.2}/>
            </linearGradient>
          </defs>
        </AreaChart>
      </ResponsiveContainer>
    </ChartContainer>
  );

  // Load and House Count chart
  const LoadHouseChart = () => (
    <ChartContainer title="Load vs Usage Count">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={histData}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="tick" />
          <YAxis yAxisId="left" />
          <YAxis yAxisId="right" orientation="right" />
          <Tooltip 
            contentStyle={{
              backgroundColor: 'rgba(255, 255, 255, 0.95)',
              border: '1px solid #667eea',
              borderRadius: '8px',
              boxShadow: '0 4px 6px rgba(102, 126, 234, 0.2)'
            }}
          />
          <Legend />          <Line 
            yAxisId="left"
            type="monotone" 
            dataKey="load" 
            stroke="#667eea" 
            strokeWidth={3}
            name="Load (kW)"
            dot={{ fill: '#667eea', strokeWidth: 2, r: 4 }}
          />
          <Line 
            yAxisId="right"
            type="monotone" 
            dataKey="houses" 
            stroke="#764ba2" 
            strokeWidth={3}
            name="Users Count"
            dot={{ fill: '#764ba2', strokeWidth: 2, r: 4 }}
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
            <YAxis />            <Tooltip formatter={(value) => [`${value?.toFixed(1)} kW`, 'Predicted Load']} 
              contentStyle={{
                backgroundColor: 'rgba(255, 255, 255, 0.95)',
                border: '1px solid #667eea',
                borderRadius: '8px',
                boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)'
              }}
            />
            <Bar dataKey="forecast" fill="url(#forecastGradient)" />
            <defs>
              <linearGradient id="forecastGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#667eea" stopOpacity={0.9}/>
                <stop offset="95%" stopColor="#764ba2" stopOpacity={0.6}/>
              </linearGradient>
            </defs>            {forecastChartData[0]?.current && (
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
      { name: 'Admin', value: 60, color: '#667eea' },
      { name: 'FOC', value: 25, color: '#764ba2' },
      { name: 'FOE', value: 10, color: '#3b82f6' },
      { name: 'FOB', value: 5, color: '#6366f1' },
    ];

    return (
      <ChartContainer title="Power Distribution by Sector (NSBM)">
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
            <Tooltip formatter={(value) => [`${value}%`, 'Share']}
              contentStyle={{
                backgroundColor: 'rgba(255, 255, 255, 0.95)',
                border: '1px solid #667eea',
                borderRadius: '8px',
                boxShadow: '0 4px 6px rgba(102, 126, 234, 0.2)'
              }}
            />
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
