import React, { useEffect, useState } from 'react';
import { zonesService } from '../services/api';

export default function Zones() {
  const [zones, setZones] = useState([]);
  const [summary, setSummary] = useState([]);

  useEffect(() => {
    const load = async () => {
      try {
        const l = await zonesService.list();
        const s = await zonesService.summary();
        setZones(l.zones || []);
        setSummary(s.categories || []);
      } catch (e) {}
    };
    load();
  }, []);

  return (
    <div className="card">
      <h2>University Zones</h2>
      <div style={{display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: 12}}>
        {summary.map((c) => (
          <div key={c.category} className="stat-card">
            <div className="stat-title">{c.category}</div>
            <div className="stat-value">{Math.round(c.total_load || 0)} kW</div>
            <div className="stat-desc">Avg Voltage: {Math.round(c.avg_voltage || 0)} V</div>
          </div>
        ))}
      </div>

      <table style={{width:'100%', marginTop: 16}}>
        <thead>
          <tr>
            <th align="left">Zone</th>
            <th align="left">Category</th>
            <th align="right">Voltage</th>
            <th align="right">Load</th>
            <th align="left">Updated</th>
            <th align="left">Status</th>
          </tr>
        </thead>
        <tbody>
          {zones.map((z) => (
            <tr key={z.id}>
              <td>{z.name}</td>
              <td>{z.category}</td>
              <td align="right">{z.latest?.voltage != null ? Math.round(z.latest.voltage) : '-'}</td>
              <td align="right">{z.latest?.load != null ? Math.round(z.latest.load) : '-'}</td>
              <td>{z.latest?.timestamp ? new Date(z.latest.timestamp).toLocaleString() : '-'}</td>
              <td>{z.status}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
