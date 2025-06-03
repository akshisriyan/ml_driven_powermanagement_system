import React from 'react';
import { Zap, RefreshCw } from 'lucide-react';

const Header = ({ onRefresh, lastUpdated, isRefreshing }) => {
  return (
    <header className="metric-card mb-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="p-2 bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg shadow-lg">
              <Zap className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-white bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
                ML-Driven Power Grid Management
              </h1>
              <p className="text-sm text-gray-300">
                Real-time monitoring and predictive analytics dashboard
              </p>
              
            </div>
          </div>

          <div className="flex items-center space-x-4">
            {lastUpdated && (
              <div className="text-sm text-gray-300">
                Last updated: {new Date(lastUpdated).toLocaleTimeString()}
              </div>
            )}
            <button
              onClick={onRefresh}
              disabled={isRefreshing}
              className={`
                btn-primary flex items-center space-x-2 px-4 py-2 rounded-lg font-medium transition-all duration-200
                ${isRefreshing
                  ? 'opacity-50 cursor-not-allowed'
                  : 'hover:scale-105 hover:shadow-lg hover:shadow-blue-500/25'
                }
              `}
            >
              <RefreshCw className={`w-4 h-4 ${isRefreshing ? 'animate-spin' : ''}`} />
              <span>{isRefreshing ? 'Refreshing...' : 'Refresh'}</span>
            </button>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;
