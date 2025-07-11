import React from 'react';

const GridStatus = ({ gridData, loading }) => {
  if (loading) {
    return (
      <div className="grid-status-container">
        <div className="grid-status-cards">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="grid-status-card loading">
              <div className="card-icon">⚡</div>
              <div className="card-content">
                <div className="card-value skeleton"></div>
                <div className="card-label skeleton"></div>
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  const voltage = gridData?.total_voltage || 0;
  const load = gridData?.total_load || 0;
  const houses = gridData?.house_count || 0;
  const tick = gridData?.tick || 0;

  // Generate sample detailed data for the table
  const detailedData = [
    { id: 1, zone: 'Zone A', voltage: Math.round(voltage * 0.25), load: Math.round(load * 0.3), houses: Math.round(houses * 0.2), status: 'Active' },
    { id: 2, zone: 'Zone B', voltage: Math.round(voltage * 0.22), load: Math.round(load * 0.25), houses: Math.round(houses * 0.25), status: 'Active' },
    { id: 3, zone: 'Zone C', voltage: Math.round(voltage * 0.28), load: Math.round(load * 0.2), houses: Math.round(houses * 0.3), status: 'Active' },
    { id: 4, zone: 'Zone D', voltage: Math.round(voltage * 0.25), load: Math.round(load * 0.25), houses: Math.round(houses * 0.25), status: 'Maintenance' },
  ];

  return (
    <div className="grid-status-container">
      <div className="grid-status-cards">
        <div className="grid-status-card">
          <div className="card-icon voltage">⚡</div>
          <div className="card-content">
            <div className="card-value">{voltage.toLocaleString()}</div>
            <div className="card-label">Total Voltage (V)</div>
          </div>
        </div>

        <div className="grid-status-card">
          <div className="card-icon load">🔋</div>
          <div className="card-content">
            <div className="card-value">{load.toLocaleString()}</div>
            <div className="card-label">Total Load (kW)</div>
          </div>
        </div>

        <div className="grid-status-card">
          <div className="card-icon houses">🏠</div>
          <div className="card-content">
            <div className="card-value">{houses}</div>
            <div className="card-label">Connected Houses</div>
          </div>
        </div>

        <div className="grid-status-card">
          <div className="card-icon tick">⏱️</div>
          <div className="card-content">
            <div className="card-value">{tick}</div>
            <div className="card-label">System Tick</div>
          </div>
        </div>
      </div>

      {/* Detailed Grid Data Table */}
      <div className="grid-data-table">
        <div className="table-header">
          <h3>🏗️ Grid Zone Details</h3>
          <div className="table-stats">
            <span className="stat-badge active">4 Zones Active</span>
            <span className="stat-badge maintenance">1 Under Maintenance</span>
          </div>
        </div>
        <div className="table-container">
          <table className="data-table">
            <thead>
              <tr>
                <th>Zone</th>
                <th>Voltage (V)</th>
                <th>Load (kW)</th>
                <th>Houses</th>
                <th>Status</th>
                <th>Efficiency</th>
              </tr>
            </thead>
            <tbody>
              {detailedData.map((row) => (
                <tr key={row.id} className={row.status === 'Active' ? 'active-row' : 'maintenance-row'}>
                  <td>
                    <div className="zone-cell">
                      <span className="zone-icon">🏢</span>
                      {row.zone}
                    </div>
                  </td>
                  <td className="voltage-cell">{row.voltage.toLocaleString()}</td>
                  <td className="load-cell">{row.load.toLocaleString()}</td>
                  <td className="houses-cell">{row.houses}</td>
                  <td>
                    <span className={`status-badge ${row.status.toLowerCase()}`}>
                      {row.status === 'Active' ? '✅' : '🔧'} {row.status}
                    </span>
                  </td>
                  <td className="efficiency-cell">
                    <div className="efficiency-bar">
                      <div className="efficiency-fill" style={{ width: `${85 + Math.random() * 15}%` }}></div>
                      <span className="efficiency-text">{Math.round(85 + Math.random() * 15)}%</span>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default GridStatus;
