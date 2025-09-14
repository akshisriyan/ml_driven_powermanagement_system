import React, { useEffect, useState } from 'react';
import api, { controlService } from '../services/api';

export default function TopNotification() {
  const [health, setHealth] = useState(null);
  const [loading, setLoading] = useState(false);
  const role = localStorage.getItem('role');

  const loadHealth = async () => {
    try {
  const { data } = await api.get('/api/grid/system-health');
  setHealth(data);
    } catch (e) {
      // ignore
    }
  };

  useEffect(() => {
    loadHealth();
    const id = setInterval(loadHealth, 15000);
    return () => clearInterval(id);
  }, []);

  if (!health || health.status === 'healthy') return null;

  const isAdmin = role === 'admin';
  const showAction = isAdmin && health.recommended_action === 'enable_generator' && !health.generator?.enabled;

  const enableGenerator = async () => {
    try {
      setLoading(true);
      await controlService.setGenerator(true);
      await loadHealth();
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{
      position: 'sticky', top: 0, zIndex: 1000,
      background: health.status === 'critical' ? '#ffebe9' : '#fff8e1',
      color: '#111', borderBottom: '1px solid #ddd', padding: '8px 16px'
    }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <strong>System {health.status.toUpperCase()}</strong>
          <span style={{ marginLeft: 8 }}>
            Avg Voltage: {Math.round(health.averages.voltage)} V · Avg Load: {Math.round(health.averages.load)} kW
          </span>
        </div>
        {showAction && (
          <button onClick={enableGenerator} disabled={loading} style={{
            background: '#0a7', color: '#fff', border: 'none', padding: '6px 12px', borderRadius: 4,
            cursor: 'pointer'
          }}>
            {loading ? 'Enabling…' : 'Enable Generator Now'}
          </button>
        )}
      </div>
    </div>
  );
}
