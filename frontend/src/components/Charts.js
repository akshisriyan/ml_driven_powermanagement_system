import React from 'react';

const Charts = ({ gridData, forecastData, historicalData, loading }) => {
  if (loading) {
    return (
      <div className="charts-container">
        <div className="chart-card loading">
          <div className="chart-header">
            <h3>Power Distribution</h3>
          </div>
          <div className="chart-content skeleton"></div>
        </div>
        <div className="chart-card loading">
          <div className="chart-header">
            <h3>Load Trends</h3>
          </div>
          <div className="chart-content skeleton"></div>
        </div>
      </div>
    );
  }

  const voltage = gridData?.total_voltage || 0;
  const load = gridData?.total_load || 0;
  const efficiency = voltage > 0 ? ((load / voltage) * 100).toFixed(1) : 0;

  // Generate hourly data for the last 24 hours
  const hourlyData = Array.from({ length: 24 }, (_, i) => ({
    hour: i,
    voltage: Math.round(voltage * (0.9 + Math.random() * 0.2)),
    load: Math.round(load * (0.8 + Math.random() * 0.4)),
    efficiency: Math.round(80 + Math.random() * 20),
    time: `${i.toString().padStart(2, '0')}:00`,
  }));

  return (
    <div className="charts-container">
      <div className="chart-card">
        <div className="chart-header">
          <h3>⚡ Power Distribution</h3>
        </div>
        <div className="chart-content">
          <div className="power-meter">
            <div className="meter-circle">
              <div className="meter-value">{voltage.toLocaleString()}</div>
              <div className="meter-label">Volts</div>
            </div>
            <div className="meter-stats">
              <div className="stat-item">
                <div className="stat-value">{load.toLocaleString()}</div>
                <div className="stat-label">Load (kW)</div>
              </div>
              <div className="stat-item">
                <div className="stat-value">{efficiency}%</div>
                <div className="stat-label">Efficiency</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="chart-card">
        <div className="chart-header">
          <h3>📊 Load Trends</h3>
        </div>
        <div className="chart-content">
          <div className="trend-chart">
            <div className="trend-bars">
              {[85, 92, 78, 95, 88, 91, 87, 93, 89, 96].map((value, index) => (
                <div key={index} className="trend-bar">
                  <div 
                    className="bar-fill" 
                    style={{ height: `${value}%` }}
                  ></div>
                  <div className="bar-label">{index + 1}</div>
                </div>
              ))}
            </div>
            <div className="trend-info">
              <div className="trend-stat">
                <span className="trend-label">Current Load:</span>
                <span className="trend-value">{load} kW</span>
              </div>
              <div className="trend-stat">
                <span className="trend-label">Peak Load:</span>
                <span className="trend-value">{Math.round(load * 1.2)} kW</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* 24-Hour Performance Table */}
      <div className="chart-card full-width">
        <div className="chart-header">
          <h3>📈 24-Hour Performance Data</h3>
          <div className="chart-controls">
            <button className="chart-btn active">Hourly</button>
            <button className="chart-btn">Daily</button>
            <button className="chart-btn">Weekly</button>
          </div>
        </div>
        <div className="chart-content">
          <div className="performance-table-container">
            <table className="performance-table">
              <thead>
                <tr>
                  <th>Time</th>
                  <th>Voltage (V)</th>
                  <th>Load (kW)</th>
                  <th>Efficiency (%)</th>
                  <th>Status</th>
                  <th>Trend</th>
                </tr>
              </thead>
              <tbody>
                {hourlyData.slice(0, 12).map((data, index) => (
                  <tr key={index}>
                    <td className="time-cell">{data.time}</td>
                    <td className="voltage-cell">{data.voltage.toLocaleString()}</td>
                    <td className="load-cell">{data.load.toLocaleString()}</td>
                    <td className="efficiency-cell">
                      <div className="efficiency-bar-small">
                        <div 
                          className="efficiency-fill-small" 
                          style={{ width: `${data.efficiency}%` }}
                        ></div>
                        <span className="efficiency-text-small">{data.efficiency}%</span>
                      </div>
                    </td>
                    <td>
                      <span className={`status-indicator ${data.efficiency > 85 ? 'optimal' : 'normal'}`}>
                        {data.efficiency > 85 ? '🟢 Optimal' : '🟡 Normal'}
                      </span>
                    </td>
                    <td className="trend-cell">
                      {index > 0 && data.load > hourlyData[index - 1].load ? '📈' : '📉'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Charts;
