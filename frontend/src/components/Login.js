import React, { useState } from 'react';
import { Lock, User, Eye, EyeOff, Zap, Shield } from 'lucide-react';

const Login = ({ onLogin }) => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);

    // Simulate authentication delay
    await new Promise(resolve => setTimeout(resolve, 1000));

    if (username === 'admin' && password === '123') {
      onLogin();
    } else {
      setError('Invalid username or password');
    }
    setIsLoading(false);
  };
  return (
    <div className="login-container">
      {/* Animated Background Elements */}
      <div className="login-background">
        <div className="bg-shape bg-shape-1"></div>
        <div className="bg-shape bg-shape-2"></div>
        <div className="bg-shape bg-shape-3"></div>
      </div>

      {/* Grid Pattern Overlay */}
      <div className="bg-grid-pattern"></div>

      {/* Login Card */}
      <div className="login-card">
        <div className="metric-card">
          {/* Header */}
          <div className="login-header">
            <div className="login-icon-container">
              <div className="login-icon">
                <Zap className="icon-large" />
              </div>
              <div className="login-badge">
                <Shield className="icon-small" />
              </div>
            </div>
            <h1 className="login-title">
              Power Grid Admin
            </h1>
            <p className="login-subtitle">
              ML-Driven Power Management System
            </p>
          </div>

          {/* Login Form */}
          <form onSubmit={handleSubmit} className="login-form">
            {/* Username Field */}
            <div className="form-group">
              <label className="form-label">
                Username
              </label>
              <div className="input-container">
                <User className="input-icon" />
                <input
                  type="text"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  className="form-input"
                  placeholder="Enter your username"
                  required
                />
              </div>
            </div>

            {/* Password Field */}
            <div className="form-group">
              <label className="form-label">
                Password
              </label>
              <div className="input-container">
                <Lock className="input-icon" />
                <input
                  type={showPassword ? "text" : "password"}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="form-input"
                  placeholder="Enter your password"
                  required
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="toggle-password"
                >
                  {showPassword ? <EyeOff className="icon-small" /> : <Eye className="icon-small" />}
                </button>
              </div>
            </div>

            {/* Error Message */}
            {error && (
              <div className="error-message">
                {error}
              </div>
            )}

            {/* Login Button */}
            <button
              type="submit"
              disabled={isLoading}
              className={`login-button ${isLoading ? 'loading' : ''}`}
            >
              {isLoading ? (
                <div className="loading-content">
                  <div className="spinner"></div>
                  Authenticating...
                </div>
              ) : (
                'Sign In'
              )}
            </button>
          </form>

          {/* Footer */}
          <div className="login-footer">
            <p className="footer-text">
              Secure access to power grid management
            </p>
            <div className="footer-dots">
              <div className="dot dot-1"></div>
              <div className="dot dot-2"></div>
              <div className="dot dot-3"></div>
            </div>
          </div>
        </div>

        {/* Demo Credentials */}
        <div className="demo-credentials">
          <h3 className="demo-title">
            <Shield className="icon-small" />
            Demo Credentials
          </h3>
          <div className="demo-info">
            <p><strong>Username:</strong> admin</p>
            <p><strong>Password:</strong> 123</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Login;
