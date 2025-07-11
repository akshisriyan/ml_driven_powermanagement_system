import React from 'react';

export const LoadingScreen = ({ message = "Loading..." }) => {
  return (
    <div className="loading-screen">
      <div className="loading-content">
        <div className="loading-spinner">
          <div className="spinner-ring"></div>
          <div className="spinner-ring"></div>
          <div className="spinner-ring"></div>
        </div>
        <div className="loading-text">
          <h2>{message}</h2>
          <p>Please wait while we initialize the system...</p>
        </div>
      </div>
    </div>
  );
};

export const LoadingSpinner = ({ size = 'medium' }) => {
  return (
    <div className={`loading-spinner-small ${size}`}>
      <div className="spinner-dot"></div>
      <div className="spinner-dot"></div>
      <div className="spinner-dot"></div>
    </div>
  );
};

export default LoadingScreen;
