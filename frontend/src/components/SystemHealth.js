import React from 'react';
import { Shield, ShieldCheck, ShieldAlert, ShieldX, Database, Clock, Activity } from 'lucide-react';

const HealthIndicator = ({ status, label, value, unit = "" }) => {
  const getStatusConfig = () => {
    switch (status) {
      case 'healthy':
      case 'good':
        return {
          icon: ShieldCheck,
          color: 'text-green-400',
          bgColor: 'bg-green-500/20',
          borderColor: 'border-green-500/30'
        };
      case 'warning':
        return {
          icon: ShieldAlert,
          color: 'text-yellow-400',
          bgColor: 'bg-yellow-500/20',
          borderColor: 'border-yellow-500/30'
        };
      case 'critical':
      case 'danger':
        return {
          icon: ShieldX,
          color: 'text-red-400',
          bgColor: 'bg-red-500/20',
          borderColor: 'border-red-500/30'
        };
      default:
        return {
          icon: Shield,
          color: 'text-blue-400',
          bgColor: 'bg-blue-500/20',
          borderColor: 'border-blue-500/30'
        };
    }
  };

  const config = getStatusConfig();
  const Icon = config.icon;

  return (
    <div className={`metric-card p-4 rounded-lg border backdrop-blur-md ${config.borderColor} ${config.bgColor}`}>
      <div className="flex items-center space-x-3">
        <Icon className={`w-5 h-5 ${config.color}`} />
        <div>
          <p className="text-sm font-medium text-gray-200">{label}</p>
          <p className={`text-lg font-bold ${config.color}`}>
            {typeof value === 'number' ? value.toLocaleString() : value}
            {unit && <span className="text-sm ml-1">{unit}</span>}
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
        <div className="flex items-center space-x-2 mb-4">
          <Activity className="w-5 h-5 text-blue-400" />
          <h3 className="text-lg font-semibold text-white bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">System Health</h3>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {[...Array(3)].map((_, i) => (
            <div key={i} className="metric-card p-4 rounded-lg animate-pulse">
              <div className="flex items-center space-x-3">
                <div className="w-5 h-5 bg-blue-300/30 rounded"></div>
                <div>
                  <div className="h-4 bg-blue-300/30 rounded w-20 mb-1"></div>
                  <div className="h-5 bg-blue-300/30 rounded w-16"></div>
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
        <div className="flex items-center space-x-2 mb-4">
          <Activity className="w-5 h-5 text-blue-400" />
          <h3 className="text-lg font-semibold text-white bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">System Health</h3>
        </div>
        <div className="text-center py-8">
          <ShieldX className="w-12 h-12 text-gray-400 mx-auto mb-2" />
          <p className="text-gray-300">No health data available</p>
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
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center space-x-2">
          <Activity className="w-5 h-5 text-blue-400" />
          <h3 className="text-lg font-semibold text-white bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">System Health</h3>
        </div>
        <div className="text-sm text-gray-300">
          {healthData.timestamp && (
            <>Updated: {new Date(healthData.timestamp).toLocaleTimeString()}</>
          )}
        </div>
      </div>

      {/* Overall Status */}
      <div className="mb-6">
        <HealthIndicator
          status={healthData.status}
          label="Overall System Status"
          value={getOverallStatus()}
        />
      </div>

      {/* System Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <HealthIndicator
          status="good"
          label="Total Records"
          value={healthData.total_records}
          icon={Database}
        />
        <HealthIndicator
          status="good"
          label="Latest Tick"
          value={healthData.latest_tick}
          icon={Clock}
        />
        <HealthIndicator
          status={healthData.averages?.voltage > 20000 ? 'good' : 'warning'}
          label="Avg Voltage"
          value={healthData.averages?.voltage?.toFixed(1)}
          unit="V"
        />
      </div>

      {/* Performance Averages */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
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
      </div>

      {/* System Recommendations */}
      <div className="mt-6 metric-card">
        <h4 className="text-sm font-medium text-white mb-2 bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">System Recommendations</h4>
        <div className="space-y-1 text-xs text-gray-300">
          {healthData.status === 'healthy' && (
            <div className="flex items-center space-x-2">
              <div className="w-2 h-2 bg-green-400 rounded-full"></div>
              <span>All systems operating within normal parameters</span>
            </div>
          )}
          {healthData.status === 'warning' && (
            <>
              <div className="flex items-center space-x-2">
                <div className="w-2 h-2 bg-yellow-400 rounded-full"></div>
                <span>Monitor voltage levels closely</span>
              </div>
              <div className="flex items-center space-x-2">
                <div className="w-2 h-2 bg-yellow-400 rounded-full"></div>
                <span>Consider load balancing adjustments</span>
              </div>
            </>
          )}
          {healthData.status === 'critical' && (
            <>
              <div className="flex items-center space-x-2">
                <div className="w-2 h-2 bg-red-400 rounded-full"></div>
                <span>Immediate attention required</span>
              </div>
              <div className="flex items-center space-x-2">
                <div className="w-2 h-2 bg-red-400 rounded-full"></div>
                <span>Check grid stability</span>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
};

export default SystemHealth;
