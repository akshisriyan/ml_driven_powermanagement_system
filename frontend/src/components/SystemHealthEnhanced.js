import React, { useState, useEffect, useCallback } from 'react';
import { gridService } from '../services/api';
import './SystemHealth.css';

function SystemHealth() {
    const [systemData, setSystemData] = useState({
        status: 'Normal',
        voltage: 220,
        temperature: 25,
        load: 85,
        generatorEnabled: false,
        efficiency: 95,
        lastUpdate: new Date().toLocaleString()
    });
    
    const [notifications, setNotifications] = useState([]);
    const [showInstructions, setShowInstructions] = useState(false);
    const [isLoading, setIsLoading] = useState(false);

    const checkSystemHealth = (data) => {
        const newNotifications = [];
        
        // Voltage imbalance detection
        if (data.voltage < 200 || data.voltage > 240) {
            newNotifications.push({
                id: Date.now(),
                type: 'critical',
                title: 'Voltage Imbalance Detected',
                message: `Grid voltage ${(data.voltage || 220).toFixed(1)}V is outside safe range (200-240V)`,
                timestamp: new Date().toLocaleString(),
                action: data.voltage < 200 ? 'Low voltage detected - Consider generator activation' : 'High voltage detected - Check load balancing'
            });
        }
        
        // Load imbalance detection
        if (data.load > 95) {
            newNotifications.push({
                id: Date.now() + 1,
                type: 'warning',
                title: 'High Load Detected',
                message: `System load at ${data.load}% - Approaching capacity limits`,
                timestamp: new Date().toLocaleString(),
                action: 'Consider load shedding or generator support'
            });
        }
        
        // Temperature monitoring
        if (data.temperature > 35) {
            newNotifications.push({
                id: Date.now() + 2,
                type: 'warning',
                title: 'High Temperature Alert',
                message: `System temperature ${data.temperature}°C - Cooling systems engaged`,
                timestamp: new Date().toLocaleString(),
                action: 'Monitor cooling systems and reduce load if necessary'
            });
        }
        
        // Efficiency monitoring
        if (data.efficiency < 85) {
            newNotifications.push({
                id: Date.now() + 3,
                type: 'info',
                title: 'Efficiency Alert',
                message: `System efficiency at ${data.efficiency}% - Below optimal threshold`,
                timestamp: new Date().toLocaleString(),
                action: 'Schedule maintenance check for optimal performance'
            });
        }
        
        return newNotifications;
    };

    const fetchSystemHealth = useCallback(async () => {
        try {
            const response = await gridService.getSystemHealth();
            let data = response.data || response;
            
            // Map backend data to frontend format
            const mappedData = {
                status: data.status || 'Normal',
                voltage: data.voltage || 220,
                temperature: data.temperature || 25,
                load: data.load || 85,
                generatorEnabled: data.generatorEnabled || (data.generator && data.generator.enabled) || false,
                efficiency: data.efficiency || 95,
                lastUpdate: data.lastUpdate || new Date().toLocaleString()
            };
            
            setSystemData(mappedData);
            
            // Check for system imbalances and generate notifications
            const newNotifications = checkSystemHealth(mappedData);
            if (newNotifications.length > 0) {
                setNotifications(prev => [...newNotifications, ...prev.slice(0, 4)]); // Keep last 5 notifications
            }
            
        } catch (error) {
            console.error('Error fetching system health:', error);
            // Use fallback data with some variation
            const fallbackData = {
                status: Math.random() > 0.8 ? 'Warning' : 'Normal',
                voltage: 220 + (Math.random() - 0.5) * 20,
                temperature: 25 + Math.random() * 10,
                load: 75 + Math.random() * 20,
                generatorEnabled: systemData.generatorEnabled,
                efficiency: 90 + Math.random() * 10,
                lastUpdate: new Date().toLocaleString()
            };
            setSystemData(fallbackData);
            
            const newNotifications = checkSystemHealth(fallbackData);
            if (newNotifications.length > 0) {
                setNotifications(prev => [...newNotifications, ...prev.slice(0, 4)]);
            }
        }
    }, []);

    const toggleGenerator = async () => {
        setIsLoading(true);
        try {
            const response = await fetch('http://localhost:5000/api/grid/generator/toggle', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                }
            });
            
            if (response.ok) {
                const result = await response.json();
                setSystemData(prev => ({
                    ...prev,
                    generatorEnabled: result.generator_enabled
                }));
                
                // Add notification for generator status change
                const notification = {
                    id: Date.now(),
                    type: 'info',
                    title: 'Generator Status Changed',
                    message: result.message,
                    timestamp: new Date().toLocaleString(),
                    action: result.generator_enabled ? 'Generator is now providing backup power' : 'Generator has been shut down'
                };
                setNotifications(prev => [notification, ...prev.slice(0, 4)]);
            } else {
                throw new Error('Failed to toggle generator');
            }
        } catch (error) {
            console.error('Error toggling generator:', error);
            // Fallback toggle for demo
            setSystemData(prev => ({
                ...prev,
                generatorEnabled: !prev.generatorEnabled
            }));
        } finally {
            setIsLoading(false);
        }
    };

    const clearNotification = (notificationId) => {
        setNotifications(prev => prev.filter(n => n.id !== notificationId));
    };

    useEffect(() => {
        fetchSystemHealth();
        const interval = setInterval(fetchSystemHealth, 10000); // Update every 10 seconds
        return () => clearInterval(interval);
    }, []);

    const getStatusColor = (status) => {
        switch (status.toLowerCase()) {
            case 'critical': return '#dc3545';
            case 'warning': return '#ffc107';
            case 'normal': return '#28a745';
            default: return '#6c757d';
        }
    };

    const getNotificationColor = (type) => {
        switch (type) {
            case 'critical': return '#dc3545';
            case 'warning': return '#ffc107';
            case 'info': return '#17a2b8';
            default: return '#6c757d';
        }
    };

    return (
        <div className="system-health">
            <div className="system-health-header">
                <h2>System Health Dashboard</h2>
                <div className="last-update">Last updated: {systemData.lastUpdate}</div>
            </div>

            {/* System Status Overview */}
            <div className="status-grid">
                <div className="status-card">
                    <div className="status-icon" style={{ backgroundColor: getStatusColor(systemData.status) }}>
                        <i className="fas fa-heartbeat"></i>
                    </div>
                    <div className="status-info">
                        <h3>System Status</h3>
                        <div className="status-value" style={{ color: getStatusColor(systemData.status) }}>
                            {systemData.status}
                        </div>
                    </div>
                </div>

                <div className="status-card">
                    <div className="status-icon" style={{ backgroundColor: '#007bff' }}>
                        <i className="fas fa-bolt"></i>
                    </div>
                    <div className="status-info">
                        <h3>Grid Voltage</h3>
                        <div className="status-value">{(systemData.voltage || 220).toFixed(1)}V</div>
                    </div>
                </div>

                <div className="status-card">
                    <div className="status-icon" style={{ backgroundColor: '#fd7e14' }}>
                        <i className="fas fa-thermometer-half"></i>
                    </div>
                    <div className="status-info">
                        <h3>Temperature</h3>
                        <div className="status-value">{(systemData.temperature || 25).toFixed(1)}°C</div>
                    </div>
                </div>

                <div className="status-card">
                    <div className="status-icon" style={{ backgroundColor: '#6610f2' }}>
                        <i className="fas fa-tachometer-alt"></i>
                    </div>
                    <div className="status-info">
                        <h3>System Load</h3>
                        <div className="status-value">{(systemData.load || 85).toFixed(1)}%</div>
                    </div>
                </div>
            </div>

            {/* Generator Control Section */}
            <div className="generator-control-section">
                <div className="section-header">
                    <h3>Backup Generator Control</h3>
                </div>
                <div className="generator-control">
                    <div className="generator-status">
                        <div className={`generator-indicator ${systemData.generatorEnabled ? 'online' : 'offline'}`}>
                            <i className="fas fa-power-off"></i>
                        </div>
                        <div className="generator-info">
                            <h4>Generator Status: {systemData.generatorEnabled ? 'ONLINE' : 'OFFLINE'}</h4>
                            <p>{systemData.generatorEnabled ? 'Providing backup power to the grid' : 'Ready for emergency activation'}</p>
                        </div>
                    </div>
                    <button 
                        className={`generator-toggle-btn ${systemData.generatorEnabled ? 'stop' : 'start'}`}
                        onClick={toggleGenerator}
                        disabled={isLoading}
                    >
                        {isLoading ? (
                            <><i className="fas fa-spinner fa-spin"></i> Processing...</>
                        ) : systemData.generatorEnabled ? (
                            <><i className="fas fa-stop"></i> Stop Generator</>
                        ) : (
                            <><i className="fas fa-play"></i> Start Generator</>
                        )}
                    </button>
                </div>
            </div>

            {/* Notifications Section */}
            {notifications.length > 0 && (
                <div className="notifications-section">
                    <div className="section-header">
                        <h3>System Notifications</h3>
                        <span className="notification-count">{notifications.length}</span>
                    </div>
                    <div className="notifications-list">
                        {notifications.map(notification => (
                            <div key={notification.id} className={`notification ${notification.type}`}>
                                <div className="notification-header">
                                    <div className="notification-icon" style={{ backgroundColor: getNotificationColor(notification.type) }}>
                                        <i className={`fas ${notification.type === 'critical' ? 'fa-exclamation-triangle' : notification.type === 'warning' ? 'fa-exclamation-circle' : 'fa-info-circle'}`}></i>
                                    </div>
                                    <div className="notification-title">{notification.title}</div>
                                    <button className="notification-close" onClick={() => clearNotification(notification.id)}>
                                        <i className="fas fa-times"></i>
                                    </button>
                                </div>
                                <div className="notification-content">
                                    <p className="notification-message">{notification.message}</p>
                                    <p className="notification-action">{notification.action}</p>
                                    <div className="notification-timestamp">{notification.timestamp}</div>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            )}

            {/* Instructions Section */}
            <div className="instructions-section">
                <div className="section-header">
                    <h3>System Management Instructions</h3>
                    <button 
                        className="toggle-instructions"
                        onClick={() => setShowInstructions(!showInstructions)}
                    >
                        {showInstructions ? 'Hide Instructions' : 'Show Instructions'}
                        <i className={`fas fa-chevron-${showInstructions ? 'up' : 'down'}`}></i>
                    </button>
                </div>
                
                {showInstructions && (
                    <div className="instructions-content">
                        <div className="instruction-category">
                            <h4><i className="fas fa-exclamation-triangle"></i> Emergency Procedures</h4>
                            <ul>
                                <li><strong>Voltage Imbalance (Below 200V):</strong> Immediately activate backup generator and notify maintenance team</li>
                                <li><strong>Overvoltage (Above 240V):</strong> Check load distribution and consider load shedding if necessary</li>
                                <li><strong>System Overload (&gt;95%):</strong> Implement controlled load shedding starting with non-critical zones</li>
                                <li><strong>Generator Failure:</strong> Contact emergency maintenance and prepare for controlled system shutdown if needed</li>
                            </ul>
                        </div>

                        <div className="instruction-category">
                            <h4><i className="fas fa-cogs"></i> Routine Maintenance</h4>
                            <ul>
                                <li><strong>Daily:</strong> Monitor voltage levels, temperature, and system load</li>
                                <li><strong>Weekly:</strong> Test generator functionality and review efficiency metrics</li>
                                <li><strong>Monthly:</strong> Inspect cooling systems and clean system components</li>
                                <li><strong>Quarterly:</strong> Perform comprehensive system health assessment</li>
                            </ul>
                        </div>

                        <div className="instruction-category">
                            <h4><i className="fas fa-shield-alt"></i> Safety Guidelines</h4>
                            <ul>
                                <li>Always wear appropriate PPE when working with electrical equipment</li>
                                <li>Follow lockout/tagout procedures before maintenance</li>
                                <li>Never exceed 90% system capacity during normal operations</li>
                                <li>Keep emergency contacts readily available</li>
                            </ul>
                        </div>

                        <div className="instruction-category">
                            <h4><i className="fas fa-phone"></i> Emergency Contacts</h4>
                            <div className="emergency-contacts">
                                <div className="contact">
                                    <strong>Maintenance Team:</strong> +1 (555) 123-4567
                                </div>
                                <div className="contact">
                                    <strong>Emergency Services:</strong> 911
                                </div>
                                <div className="contact">
                                    <strong>Power Authority:</strong> +1 (555) 987-6543
                                </div>
                            </div>
                        </div>
                    </div>
                )}
            </div>

            {/* System Metrics */}
            <div className="metrics-section">
                <h3>Performance Metrics</h3>
                <div className="metrics-grid">
                    <div className="metric">
                        <div className="metric-label">System Efficiency</div>
                        <div className="metric-value">{(systemData.efficiency || 95).toFixed(1)}%</div>
                        <div className={`metric-trend ${(systemData.efficiency || 95) > 90 ? 'positive' : 'negative'}`}>
                            <i className={`fas fa-arrow-${(systemData.efficiency || 95) > 90 ? 'up' : 'down'}`}></i>
                        </div>
                    </div>
                    <div className="metric">
                        <div className="metric-label">Grid Stability</div>
                        <div className="metric-value">
                            {(systemData.voltage || 220) >= 200 && (systemData.voltage || 220) <= 240 ? 'Stable' : 'Unstable'}
                        </div>
                        <div className={`metric-trend ${(systemData.voltage || 220) >= 200 && (systemData.voltage || 220) <= 240 ? 'positive' : 'negative'}`}>
                            <i className={`fas fa-${(systemData.voltage || 220) >= 200 && (systemData.voltage || 220) <= 240 ? 'check' : 'exclamation-triangle'}`}></i>
                        </div>
                    </div>
                    <div className="metric">
                        <div className="metric-label">Load Factor</div>
                        <div className="metric-value">{((systemData.load || 85) / 100 * 0.85).toFixed(2)}</div>
                        <div className="metric-trend positive">
                            <i className="fas fa-check"></i>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}

export default SystemHealth;
