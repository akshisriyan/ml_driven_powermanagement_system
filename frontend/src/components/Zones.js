import React, { useState, useEffect } from 'react';
import './ZoneManagement.css';

const API_BASE_URL = 'http://localhost:5000';

const ZoneManagement = () => {
  const [zones, setZones] = useState([]);
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isAdmin, setIsAdmin] = useState(false);
  const [selectedZone, setSelectedZone] = useState(null);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [showEditForm, setShowEditForm] = useState(false);
  const [showForecast, setShowForecast] = useState(false);
  const [forecast, setForecast] = useState(null);
  const [forecastLoading, setForecastLoading] = useState(false);
  
  const [formData, setFormData] = useState({
    name: '',
    category: 'faculty',
    description: '',
    location: '',
    capacity: 0,
    min_voltage: 220,
    max_voltage: 240,
    target_load: 0,
    parent_id: null
  });

  useEffect(() => {
    fetchZones();
    fetchCategories();
    checkAdminStatus();
  }, []);

  const checkAdminStatus = () => {
    const token = localStorage.getItem('token');
    if (token) {
      try {
        const payload = JSON.parse(atob(token.split('.')[1]));
        setIsAdmin(payload.role === 'admin');
      } catch (e) {
        setIsAdmin(false);
      }
    }
  };

  const fetchZones = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/zones`);
      if (!response.ok) throw new Error('Failed to fetch zones');
      const data = await response.json();
      setZones(data.zones || []);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const fetchCategories = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/categories`);
      if (!response.ok) throw new Error('Failed to fetch categories');
      const data = await response.json();
      setCategories(data.categories || []);
    } catch (err) {
      console.error('Failed to fetch categories:', err);
    }
  };

  const handleCreateZone = async (e) => {
    e.preventDefault();
    const token = localStorage.getItem('token');
    
    try {
      const response = await fetch(`${API_BASE_URL}/api/zones`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(formData)
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to create zone');
      }

      await fetchZones();
      setShowCreateForm(false);
      resetForm();
      alert('Zone created successfully!');
    } catch (err) {
      alert(`Error: ${err.message}`);
    }
  };

  const handleUpdateZone = async (e) => {
    e.preventDefault();
    if (!selectedZone) return;
    
    const token = localStorage.getItem('token');
    
    try {
      const response = await fetch(`${API_BASE_URL}/api/zones/${selectedZone.id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(formData)
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to update zone');
      }

      await fetchZones();
      setShowEditForm(false);
      setSelectedZone(null);
      resetForm();
      alert('Zone updated successfully!');
    } catch (err) {
      alert(`Error: ${err.message}`);
    }
  };

  const handleDeleteZone = async (zoneId, zoneName) => {
    if (!window.confirm(`Are you sure you want to delete zone "${zoneName}"?`)) {
      return;
    }

    const token = localStorage.getItem('token');
    
    try {
      const response = await fetch(`${API_BASE_URL}/api/zones/${zoneId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to delete zone');
      }

      await fetchZones();
      alert('Zone deleted successfully!');
    } catch (err) {
      alert(`Error: ${err.message}`);
    }
  };

  const showZoneForecast = async (zone) => {
    setSelectedZone(zone);
    setShowForecast(true);
    setForecastLoading(true);
    setForecast(null);

    try {
      const response = await fetch(`${API_BASE_URL}/api/zones/${zone.id}/forecast?horizon=daily&steps=30`);
      if (!response.ok) throw new Error('Failed to fetch forecast');
      const data = await response.json();
      setForecast(data);
    } catch (err) {
      setError(`Forecast error: ${err.message}`);
    } finally {
      setForecastLoading(false);
    }
  };

  const resetForm = () => {
    setFormData({
      name: '',
      category: 'faculty',
      description: '',
      location: '',
      capacity: 0,
      min_voltage: 220,
      max_voltage: 240,
      target_load: 0,
      parent_id: null
    });
  };

  const openEditForm = (zone) => {
    setSelectedZone(zone);
    setFormData({
      name: zone.name || '',
      category: zone.category || 'faculty',
      description: zone.description || '',
      location: zone.location || '',
      capacity: zone.capacity || 0,
      min_voltage: zone.min_voltage || 220,
      max_voltage: zone.max_voltage || 240,
      target_load: zone.target_load || 0,
      parent_id: zone.parent_id || null
    });
    setShowEditForm(true);
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'normal': return '#4CAF50';
      case 'warning': return '#FF9800';
      case 'critical': return '#F44336';
      default: return '#9E9E9E';
    }
  };

  const getStatusText = (status) => {
    switch (status) {
      case 'normal': return 'Normal';
      case 'warning': return 'Warning';
      case 'critical': return 'Critical';
      default: return 'No Data';
    }
  };

  if (loading) return <div className="loading">Loading zones...</div>;
  if (error) return <div className="error">Error: {error}</div>;

  return (
    <div className="zone-management">
      <div className="zone-header">
        <h2>Zone Management</h2>
        {isAdmin && (
          <button 
            className="btn btn-primary"
            onClick={() => setShowCreateForm(true)}
          >
            Add New Zone
          </button>
        )}
      </div>

      {/* Zone Grid */}
      <div className="zones-grid">
        {zones.map(zone => (
          <div key={zone.id} className="zone-card">
            <div className="zone-status" style={{ backgroundColor: getStatusColor(zone.status) }}>
              {getStatusText(zone.status)}
            </div>
            
            <h3>{zone.name}</h3>
            <div className="zone-info">
              <span className="category">{zone.category}</span>
              <span className="location">{zone.location || 'N/A'}</span>
            </div>
            
            <div className="zone-metrics">
              <div className="metric">
                <span>Voltage:</span>
                <span>{zone.voltage ? `${zone.voltage.toFixed(1)}V` : 'N/A'}</span>
              </div>
              <div className="metric">
                <span>Load:</span>
                <span>{zone.load ? `${zone.load.toFixed(1)}kW` : 'N/A'}</span>
              </div>
              <div className="metric">
                <span>Capacity:</span>
                <span>{zone.capacity ? `${zone.capacity}kW` : 'N/A'}</span>
              </div>
              {zone.temperature && (
                <div className="metric">
                  <span>Temperature:</span>
                  <span>{zone.temperature.toFixed(1)}°C</span>
                </div>
              )}
            </div>

            <div className="zone-actions">
              <button 
                className="btn btn-secondary"
                onClick={() => showZoneForecast(zone)}
              >
                View Forecast
              </button>
              {isAdmin && (
                <>
                  <button 
                    className="btn btn-warning"
                    onClick={() => openEditForm(zone)}
                  >
                    Edit
                  </button>
                  <button 
                    className="btn btn-danger"
                    onClick={() => handleDeleteZone(zone.id, zone.name)}
                  >
                    Delete
                  </button>
                </>
              )}
            </div>
          </div>
        ))}
      </div>

      {/* Create Zone Modal */}
      {showCreateForm && (
        <div className="modal-overlay">
          <div className="modal">
            <h3>Create New Zone</h3>
            <form onSubmit={handleCreateZone}>
              <div className="form-row">
                <input
                  type="text"
                  placeholder="Zone Name"
                  value={formData.name}
                  onChange={(e) => setFormData({...formData, name: e.target.value})}
                  required
                />
                <select
                  value={formData.category}
                  onChange={(e) => setFormData({...formData, category: e.target.value})}
                  required
                >
                  {categories.map(cat => (
                    <option key={cat.value} value={cat.value}>{cat.label}</option>
                  ))}
                </select>
              </div>
              
              <input
                type="text"
                placeholder="Description"
                value={formData.description}
                onChange={(e) => setFormData({...formData, description: e.target.value})}
              />
              
              <input
                type="text"
                placeholder="Location"
                value={formData.location}
                onChange={(e) => setFormData({...formData, location: e.target.value})}
              />
              
              <div className="form-row">
                <input
                  type="number"
                  placeholder="Capacity (kW)"
                  value={formData.capacity}
                  onChange={(e) => setFormData({...formData, capacity: parseFloat(e.target.value) || 0})}
                />
                <input
                  type="number"
                  placeholder="Target Load (kW)"
                  value={formData.target_load}
                  onChange={(e) => setFormData({...formData, target_load: parseFloat(e.target.value) || 0})}
                />
              </div>
              
              <div className="form-row">
                <input
                  type="number"
                  placeholder="Min Voltage"
                  value={formData.min_voltage}
                  onChange={(e) => setFormData({...formData, min_voltage: parseFloat(e.target.value) || 220})}
                />
                <input
                  type="number"
                  placeholder="Max Voltage"
                  value={formData.max_voltage}
                  onChange={(e) => setFormData({...formData, max_voltage: parseFloat(e.target.value) || 240})}
                />
              </div>

              <div className="modal-actions">
                <button type="submit" className="btn btn-primary">Create Zone</button>
                <button type="button" className="btn btn-secondary" onClick={() => {
                  setShowCreateForm(false);
                  resetForm();
                }}>Cancel</button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Edit Zone Modal */}
      {showEditForm && selectedZone && (
        <div className="modal-overlay">
          <div className="modal">
            <h3>Edit Zone: {selectedZone.name}</h3>
            <form onSubmit={handleUpdateZone}>
              <div className="form-row">
                <input
                  type="text"
                  placeholder="Zone Name"
                  value={formData.name}
                  onChange={(e) => setFormData({...formData, name: e.target.value})}
                  required
                />
                <select
                  value={formData.category}
                  onChange={(e) => setFormData({...formData, category: e.target.value})}
                  required
                >
                  {categories.map(cat => (
                    <option key={cat.value} value={cat.value}>{cat.label}</option>
                  ))}
                </select>
              </div>
              
              <input
                type="text"
                placeholder="Description"
                value={formData.description}
                onChange={(e) => setFormData({...formData, description: e.target.value})}
              />
              
              <input
                type="text"
                placeholder="Location"
                value={formData.location}
                onChange={(e) => setFormData({...formData, location: e.target.value})}
              />
              
              <div className="form-row">
                <input
                  type="number"
                  placeholder="Capacity (kW)"
                  value={formData.capacity}
                  onChange={(e) => setFormData({...formData, capacity: parseFloat(e.target.value) || 0})}
                />
                <input
                  type="number"
                  placeholder="Target Load (kW)"
                  value={formData.target_load}
                  onChange={(e) => setFormData({...formData, target_load: parseFloat(e.target.value) || 0})}
                />
              </div>
              
              <div className="form-row">
                <input
                  type="number"
                  placeholder="Min Voltage"
                  value={formData.min_voltage}
                  onChange={(e) => setFormData({...formData, min_voltage: parseFloat(e.target.value) || 220})}
                />
                <input
                  type="number"
                  placeholder="Max Voltage"
                  value={formData.max_voltage}
                  onChange={(e) => setFormData({...formData, max_voltage: parseFloat(e.target.value) || 240})}
                />
              </div>

              <div className="modal-actions">
                <button type="submit" className="btn btn-primary">Update Zone</button>
                <button type="button" className="btn btn-secondary" onClick={() => {
                  setShowEditForm(false);
                  setSelectedZone(null);
                  resetForm();
                }}>Cancel</button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Forecast Modal */}
      {showForecast && selectedZone && (
        <div className="modal-overlay">
          <div className="modal forecast-modal">
            <h3>Forecast for {selectedZone.name}</h3>
            
            {forecastLoading ? (
              <div className="loading">Loading forecast...</div>
            ) : forecast ? (
              <div className="forecast-content">
                <div className="forecast-section">
                  <h4>SARIMAX Voltage Forecast (30 Days)</h4>
                  {forecast.forecasts.sarimax_voltage?.error ? (
                    <div className="error">Error: {forecast.forecasts.sarimax_voltage.error}</div>
                  ) : (
                    <div className="forecast-chart">
                      <div className="chart-data">
                        {forecast.forecasts.sarimax_voltage?.forecast?.slice(0, 10).map((value, index) => (
                          <div key={index} className="forecast-point">
                            <span>Day {index + 1}:</span>
                            <span>{value.toFixed(2)}V</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>

                <div className="forecast-section">
                  <h4>SVR Load Forecast (30 Days)</h4>
                  {forecast.forecasts.svr_load?.error ? (
                    <div className="error">Error: {forecast.forecasts.svr_load.error}</div>
                  ) : (
                    <div className="forecast-chart">
                      <div className="chart-data">
                        {forecast.forecasts.svr_load?.forecast?.slice(0, 10).map((value, index) => (
                          <div key={index} className="forecast-point">
                            <span>Day {index + 1}:</span>
                            <span>{value.toFixed(2)}kW</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              </div>
            ) : (
              <div className="error">No forecast data available</div>
            )}

            <div className="modal-actions">
              <button 
                className="btn btn-secondary" 
                onClick={() => {
                  setShowForecast(false);
                  setSelectedZone(null);
                  setForecast(null);
                }}
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ZoneManagement;
