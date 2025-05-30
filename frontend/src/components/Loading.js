import React from 'react';
import { Zap } from 'lucide-react';

const LoadingSpinner = ({ size = 'md', className = '' }) => {
  const sizeClasses = {
    sm: 'w-4 h-4',
    md: 'w-6 h-6',
    lg: 'w-8 h-8',
    xl: 'w-12 h-12'
  };

  return (
    <div className={`animate-spin ${sizeClasses[size]} ${className}`}>
      <Zap className="w-full h-full text-primary-600" />
    </div>
  );
};

const LoadingScreen = ({ message = "Loading dashboard..." }) => {
  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center">
      <div className="text-center">
        <div className="mb-4 flex justify-center">
          <LoadingSpinner size="xl" />
        </div>
        <h2 className="text-xl font-semibold text-gray-800 mb-2">
          ML-Driven Power Grid Management
        </h2>
        <p className="text-gray-600">{message}</p>
        <div className="mt-6 flex justify-center space-x-1">
          {[...Array(3)].map((_, i) => (
            <div
              key={i}
              className="w-2 h-2 bg-primary-600 rounded-full animate-pulse"
              style={{ animationDelay: `${i * 0.2}s` }}
            />
          ))}
        </div>
      </div>
    </div>
  );
};

const LoadingCard = ({ title = "Loading...", height = "h-48" }) => {
  return (
    <div className={`bg-white rounded-lg shadow-sm border border-gray-200 p-6 ${height}`}>
      <div className="animate-pulse">
        <div className="flex items-center space-x-2 mb-4">
          <div className="w-5 h-5 bg-gray-300 rounded"></div>
          <div className="h-5 bg-gray-300 rounded w-32"></div>
        </div>
        <div className="space-y-3">
          <div className="h-4 bg-gray-300 rounded w-full"></div>
          <div className="h-4 bg-gray-300 rounded w-5/6"></div>
          <div className="h-4 bg-gray-300 rounded w-4/6"></div>
        </div>
      </div>
    </div>
  );
};

export { LoadingSpinner, LoadingScreen, LoadingCard };
export default LoadingSpinner;
