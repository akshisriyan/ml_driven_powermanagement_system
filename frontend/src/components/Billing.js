import React, { useEffect, useMemo, useState } from 'react';
import { billingService } from '../services/api';
import { LineChart, Line, CartesianGrid, XAxis, YAxis, Tooltip, ResponsiveContainer, BarChart, Bar, Legend } from 'recharts';

const number = (v, digits = 2) => {
  if (v === null || v === undefined || isNaN(v)) return '-';
  return Number(v).toFixed(digits);
};

const fmtMonth = (m) => m || '';

const Billing = () => {
  const [uploading, setUploading] = useState(false);
  const [summary, setSummary] = useState(null);
  const [monthly, setMonthly] = useState([]);
  const [error, setError] = useState('');

  const user = useMemo(() => {
    try { return JSON.parse(localStorage.getItem('user') || 'null'); } catch { return null; }
  }, []);
  const isAdmin = user?.role === 'admin';

  const load = async () => {
    try {
      const [s, m] = await Promise.all([
        billingService.getSummary(),
        billingService.getMonthly(),
      ]);
      setSummary(s);
      setMonthly(m || []);
      setError('');
    } catch (e) {
      console.error(e);
      setError('Failed to load billing data');
    }
  };

  useEffect(() => { load(); }, []);

  const onUpload = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setUploading(true);
    setError('');
    try {
      await billingService.uploadExcel(file);
      await load();
    } catch (e) {
      console.error(e);
      setError(e?.response?.data?.detail || 'Upload failed');
    } finally {
      setUploading(false);
      e.target.value = '';
    }
  };

  const totalSeries = useMemo(() => {
    return (monthly || []).map(r => ({
      month: fmtMonth(r.month),
      total_payable: r.total_payable || 0,
    }));
  }, [monthly]);

  const kwhSeries = useMemo(() => {
    return (monthly || []).map(r => ({
      month: fmtMonth(r.month),
      peak_kwh: r.peak_kwh || 0,
      day_kwh: r.day_kwh || 0,
      offpeak_kwh: r.offpeak_kwh || 0,
    }));
  }, [monthly]);

  return (
    <div className="charts-container" role="region" aria-label="University Billing">
      <div className="charts-header">
        <h2 className="charts-title">University Billing</h2>
        <p className="last-updated">Upload the monthly bill Excel and view summaries</p>
      </div>

      {error && (
        <div className="auth-error" role="alert">{error}</div>
      )}

      <div className="controls-section" style={{ gridTemplateColumns: '1fr 1fr' }}>
        <div className="card" role="group" aria-label="Upload">
          <h3 style={{ marginBottom: '0.75rem', color: '#111827' }}>Upload Monthly Bill (Excel)</h3>
          <p style={{ marginBottom: '0.75rem', color: '#4b5563' }}>Accepted: .xlsx, .xls</p>
          <input type="file" accept=".xlsx,.xls" onChange={onUpload} disabled={!isAdmin || uploading} />
          {!isAdmin && <p style={{ marginTop: '0.5rem', color: '#6b7280', fontSize: 12 }}>Only admins can upload.</p>}
        </div>

        <div className="card" role="group" aria-label="Summary KPIs">
          <h3 style={{ marginBottom: '0.75rem', color: '#111827' }}>Summary</h3>
          {summary ? (
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, minmax(0,1fr))', gap: '0.75rem' }}>
              <div>
                <div className="status-label">Months</div>
                <div className="status-value" style={{ color: '#111827' }}>{summary.total_months}</div>
              </div>
              <div>
                <div className="status-label">Total Payable (sum)</div>
                <div className="status-value" style={{ color: '#111827' }}>{number(summary.totals?.total_payable || 0, 2)}</div>
              </div>
              <div>
                <div className="status-label">Latest Month</div>
                <div className="status-value" style={{ color: '#111827' }}>{summary.latest?.month || '-'}</div>
              </div>
              <div>
                <div className="status-label">Latest Payable</div>
                <div className="status-value" style={{ color: '#111827' }}>{number(summary.latest?.total_payable || 0, 2)}</div>
              </div>
            </div>
          ) : (
            <div>Loading...</div>
          )}
        </div>
      </div>

      <div className="chart-section">
        <h3 style={{ marginBottom: '0.5rem', color: '#111827' }}>Total Amount Payable by Month</h3>
        <ResponsiveContainer width="100%" height={280}>
          <LineChart data={totalSeries} margin={{ top: 10, right: 20, left: 0, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="month" />
            <YAxis />
            <Tooltip />
            <Line type="monotone" dataKey="total_payable" stroke="#0d9488" strokeWidth={2} dot={false} />
          </LineChart>
        </ResponsiveContainer>
      </div>

      <div className="chart-section">
        <h3 style={{ marginBottom: '0.5rem', color: '#111827' }}>kWh Breakdown by Month</h3>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={kwhSeries} margin={{ top: 10, right: 20, left: 0, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="month" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Bar dataKey="peak_kwh" stackId="a" fill="#2563eb" />
            <Bar dataKey="day_kwh" stackId="a" fill="#10b981" />
            <Bar dataKey="offpeak_kwh" stackId="a" fill="#f59e0b" />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};

export default Billing;
