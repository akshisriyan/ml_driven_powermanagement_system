import React, { useEffect, useState } from 'react';
import { zonesService } from '../services/api';

const GridStatus = ({ gridData, loading }) => {
  const [zonesCount, setZonesCount] = useState(null);
  const [zonesPreview, setZonesPreview] = useState([]);

  useEffect(() => {
    let isMounted = true;
    (async () => {
      try {
        const list = await zonesService.list();
        if (!isMounted) return;
        const zones = list?.zones || [];
        setZonesCount(zones.length || 0);
        setZonesPreview(zones.slice(0, 4));
      } catch (e) {
        // ignore errors, fall back to mock below
      }
    })();
    return () => { isMounted = false; };
  }, []);
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
  // gridData no longer provides house_count; zones are retrieved separately
  const houses = null;
  const tick = gridData?.tick || 0;

  // Scale voltage if it's in the old 22000V range
  const scaledVoltage = voltage > 1000 ? voltage / 100 : voltage;

  // Generate sample detailed data for the table
  const detailedData = zonesPreview.length > 0
    ? zonesPreview.map((z, i) => ({
        id: z.id || i,
        zone: z.name,
        category: z.category,
        voltage: z.latest?.voltage != null ? Math.round(z.latest.voltage) : Math.round(scaledVoltage * 0.9 + (i * 10)), // Generate realistic variations around 220V
        load: z.latest?.load != null ? Math.round(z.latest.load) : Math.round(load * 0.25),
        status: (z.status || 'Active').charAt(0).toUpperCase() + (z.status || 'Active').slice(1),
      }))
    : [
      { id: 1, zone: 'Faculty of Computing', category: 'faculty', voltage: Math.round(scaledVoltage * 0.95), load: Math.round(load * 0.3), status: 'Active' },
      { id: 2, zone: 'Administration', category: 'admin', voltage: Math.round(scaledVoltage * 0.98), load: Math.round(load * 0.25), status: 'Active' },
      { id: 3, zone: 'Hostels', category: 'hostel', voltage: Math.round(scaledVoltage * 1.02), load: Math.round(load * 0.2), status: 'Active' },
      { id: 4, zone: 'Library', category: 'library', voltage: Math.round(scaledVoltage * 0.97), load: Math.round(load * 0.25), status: 'Maintenance' },
    ];

  return (
    <div className="grid-status-container">
      <div className="grid-status-cards">
        <div className="grid-status-card">
          <div className="card-icon voltage">⚡</div>
          <div className="card-content">
            <div className="card-value">{scaledVoltage.toLocaleString()}</div>
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
          <div className="card-icon houses">�</div>
          <div className="card-content">
            <div className="card-value">{zonesCount != null ? zonesCount : 0}</div>
            <div className="card-label">Active Zones</div>
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
                <th>Category</th>
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
                  <td className="houses-cell">{row.category}</td>
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
