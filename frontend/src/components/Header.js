import React from 'react';

const Header = ({ onRefresh, lastUpdated, isRefreshing }) => {
  const formatLastUpdated = (timestamp) => {
    if (!timestamp) return 'Never';
    const date = new Date(timestamp);
    return date.toLocaleTimeString();
  };

  return (
    <div className="header-container">
      <div className="header-content">
        <div className="header-status">
          <div className="status-indicator">
            <div className={`status-dot ${isRefreshing ? 'refreshing' : 'active'}`}></div>
            <span className="status-text">
              {isRefreshing ? 'Refreshing...' : 'System Online'}
            </span>
          </div>
          <div className="last-updated">
            Last updated: {formatLastUpdated(lastUpdated)}
          </div>
        </div>
        
        <div className="header-controls">
          <button 
            className={`refresh-btn ${isRefreshing ? 'refreshing' : ''}`}
            onClick={onRefresh}
            disabled={isRefreshing}
          >
            <span className="refresh-icon">🔄</span>
            {isRefreshing ? 'Refreshing...' : 'Refresh Data'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default Header;
