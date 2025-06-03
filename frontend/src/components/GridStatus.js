import React from 'react';
import { Activity, Zap, Home, TrendingUp } from 'lucide-react';

const StatusCard = ({ title, value, unit, icon: Icon, trend, status }) => {
  const getStatusColor = () => {
    switch (status) {
      case 'good': return 'text-green-600';
      case 'warning': return 'text-orange-600';
      case 'danger': return 'text-red-600';
      default: return 'text-blue-600';
    }
  };

  const getTrendColor = () => {
    if (trend > 0) return 'text-green-600';
    if (trend < 0) return 'text-red-600';
    return 'text-blue-600';
  };

  return (
    <div className="metric-card fade-in-up">
      <div style={{display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '16px'}}>
        <Icon className={`w-8 h-8 ${getStatusColor()}`} />
        {trend !== undefined && (
          <div style={{display: 'flex', alignItems: 'center'}} className={getTrendColor()}>
            <TrendingUp className={`w-4 h-4 mr-1 ${trend < 0 ? 'transform rotate-180' : ''}`} />
            <span className="text-sm font-medium">
              {Math.abs(trend).toFixed(1)}%
            </span>
          </div>
        )}
      </div>
      <div className="metric-label">{title}</div>
      <div className="metric-value">
        {typeof value === 'number' ? value.toLocaleString() : value}
      </div>
      <div className="status-unit">{unit}</div>
    </div>
  );
};

const GridStatus = ({ gridData, loading }) => {
  if (loading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        {[...Array(4)].map((_, i) => (
          <div key={i} className="p-6 rounded-lg border-2 border-gray-200 animate-pulse">
            <div className="flex items-center space-x-3">
              <div className="w-8 h-8 bg-gray-300 rounded"></div>
              <div>
                <div className="h-4 bg-gray-300 rounded w-20 mb-2"></div>
                <div className="h-6 bg-gray-300 rounded w-16"></div>
              </div>
            </div>
          </div>
        ))}
      </div>
    );
  }

  if (!gridData || Object.keys(gridData).length === 0) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <StatusCard
          title="Total Voltage"
          value="No Data"
          icon={Zap}
          status="warning"
        />
        <StatusCard
          title="Total Load"
          value="No Data"
          icon={Activity}
          status="warning"
        />
        <StatusCard
          title="House Count"
          value="No Data"
          icon={Home}
          status="warning"
        />
        <StatusCard
          title="Grid Tick"
          value="No Data"
          icon={TrendingUp}
          status="warning"
        />
      </div>
    );
  }

  const getVoltageStatus = (voltage) => {
    if (voltage > 240 * 100) return 'good';
    if (voltage > 220 * 100) return 'warning';
    return 'danger';
  };

  const getLoadStatus = (load) => {
    if (load < 1000) return 'good';
    if (load < 1500) return 'warning';
    return 'danger';
  };

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
      <StatusCard
        title="Total Voltage"
        value={gridData.total_voltage?.toFixed(1) || 0}
        unit="V"
        icon={Zap}
        status={getVoltageStatus(gridData.total_voltage)}
        trend={2.5}
      />
      <StatusCard
        title="Total Load"
        value={gridData.total_load?.toFixed(1) || 0}
        unit="kW"
        icon={Activity}
        status={getLoadStatus(gridData.total_load)}
        trend={-1.2}
      />
      <StatusCard
        title="Usage Count"
        value={gridData.house_count || 0}
        icon={Home}
        status="good"
        trend={5.8}
      />
      <StatusCard
        title="Grid Tick"
        value={gridData.tick || 0}
        icon={TrendingUp}
        status="good"
      />
    </div>
  );
};

export default GridStatus;
