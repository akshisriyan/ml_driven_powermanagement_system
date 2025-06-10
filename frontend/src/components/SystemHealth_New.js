import React from 'react';
import { Shield, ShieldCheck, ShieldAlert, ShieldX, Database, Clock, Activity } from 'lucide-react';

const HealthIndicator = ({ status, label, value, unit = "" }) => {
  const getStatusConfig = () => {
    switch (status) {
      case 'healthy':
      case 'good':
        return {
          icon: ShieldCheck,
          color: 'health-good',
          bgColor: 'health-good-bg',
          borderColor: 'health-good-border'
        };
      case 'warning':
        return {
          icon: ShieldAlert,
          color: 'health-warning',
          bgColor: 'health-warning-bg',
          borderColor: 'health-warning-border'
        };
      case 'critical':
      case 'danger':
        return {
          icon: ShieldX,
          color: 'health-critical',
          bgColor: 'health-critical-bg',
          borderColor: 'health-critical-border'
        };
      default:
        return {
          icon: Shield,
          color: 'health-normal',
          bgColor: 'health-normal-bg',
          borderColor: 'health-normal-border'
        };
    }
  };

  const config = getStatusConfig();
  const Icon = config.icon;

  return (
    <div className={`health-indicator ${config.borderColor} ${config.bgColor}`}>
      <div className="health-content">
        <Icon className={`health-icon ${config.color}`} />
        <div>
          <p className="health-label">{label}</p>
          <p className={`health-value ${config.color}`}>
            {typeof value === 'number' ? value.toLocaleString() : value}
            {unit && <span className="health-unit">{unit}</span>}
          </p>
        </div>
      </div>
    </div>
  );
};

const SystemHealth = ({ healthData, loading }) => {
  if (loading) {
    return (
      <div className="metric-card">
        <div className="health-header">
          <Activity className="health-title-icon" />
          <h3 className="health-title">System Health</h3>
        </div>
        <div className="health-grid">
          {[...Array(3)].map((_, i) => (
            <div key={i} className="health-loading">
              <div className="loading-content">
                <div className="loading-icon"></div>
                <div>
                  <div className="loading-text-1"></div>
                  <div className="loading-text-2"></div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  if (!healthData) {
    return (
      <div className="metric-card">
        <div className="health-header">
          <Activity className="health-title-icon" />
          <h3 className="health-title">System Health</h3>
        </div>
        <div className="health-empty">
          <ShieldX className="empty-icon" />
          <p className="empty-text">No health data available</p>
        </div>
      </div>
    );
  }

  const getOverallStatus = () => {
    const status = healthData.status;
    if (status === 'healthy') return 'System Operating Normally';
    if (status === 'warning') return 'System Warning Detected';
    if (status === 'critical') return 'Critical System Alert';
    return 'System Status Unknown';
  };

  return (
    <div className="metric-card">
      <div className="health-header-main">
        <div className="health-header">
          <Activity className="health-title-icon" />
          <h3 className="health-title">System Health</h3>
        </div>
        <div className="health-timestamp">
          {healthData.timestamp && (
            <>Updated: {new Date(healthData.timestamp).toLocaleTimeString()}</>
          )}
        </div>
      </div>

      {/* Overall Status */}
      <div className="health-overall">
        <HealthIndicator
          status={healthData.status}
          label="Overall System Status"
          value={getOverallStatus()}
        />
      </div>

      {/* System Metrics */}
      <div className="health-metrics-grid">
        <HealthIndicator
          status="good"
          label="Total Records"
          value={healthData.total_records}
        />
        <HealthIndicator
          status="good"
          label="Latest Tick"
          value={healthData.latest_tick}
        />
        <HealthIndicator
          status={healthData.averages?.voltage > 20000 ? 'good' : 'warning'}
          label="Avg Voltage"
          value={healthData.averages?.voltage?.toFixed(1)}
          unit="V"
        />
      </div>

      {/* Additional Metrics */}
      <div className="health-additional-grid">
        <HealthIndicator
          status={healthData.averages?.load < 1200 ? 'good' : 'warning'}
          label="Avg Load"
          value={healthData.averages?.load?.toFixed(1)}
          unit="kW"
        />
        <HealthIndicator
          status="good"
          label="Avg Houses"
          value={Math.round(healthData.averages?.houses || 0)}
        />
        <HealthIndicator
          status={healthData.status === 'healthy' ? 'good' : healthData.status}
          label="System Status"
          value={healthData.status?.charAt(0).toUpperCase() + healthData.status?.slice(1)}
        />
      </div>
    </div>
  );
};

export default SystemHealth;
