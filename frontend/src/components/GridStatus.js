import React from 'react';
import { Activity, Zap, Home, TrendingUp } from 'lucide-react';

const StatusCard = ({ title, value, unit, icon: Icon, trend, status }) => {
  const getStatusColor = () => {
    switch (status) {
      case 'good': return 'text-success-600 bg-success-50 border-success-200';
      case 'warning': return 'text-warning-600 bg-warning-50 border-warning-200';
      case 'danger': return 'text-danger-600 bg-danger-50 border-danger-200';
      default: return 'text-primary-600 bg-primary-50 border-primary-200';
    }
  };

  const getTrendColor = () => {
    if (trend > 0) return 'text-success-600';
    if (trend < 0) return 'text-danger-600';
    return 'text-gray-600';
  };

  return (
    <div className={`p-6 rounded-lg border-2 ${getStatusColor()} transition-all duration-200 hover:shadow-lg`}>
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <Icon className="w-8 h-8" />
          <div>
            <p className="text-sm font-medium opacity-75">{title}</p>
            <p className="text-2xl font-bold">
              {typeof value === 'number' ? value.toLocaleString() : value}
              {unit && <span className="text-lg ml-1">{unit}</span>}
            </p>
          </div>
        </div>
        {trend !== undefined && (
          <div className={`flex items-center ${getTrendColor()}`}>
            <TrendingUp className={`w-4 h-4 mr-1 ${trend < 0 ? 'transform rotate-180' : ''}`} />
            <span className="text-sm font-medium">
              {Math.abs(trend).toFixed(1)}%
            </span>
          </div>
        )}
      </div>
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
        title="House Count"
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
