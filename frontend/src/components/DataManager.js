import React, { useState, useRef, useEffect } from 'react';
import { gridService } from '../services/api';

const DataManager = ({ loading }) => {
  const [isUploading, setIsUploading] = useState(false);
  const [isDownloading, setIsDownloading] = useState(false);
  const [uploadStatus, setUploadStatus] = useState('');
  const [uploadError, setUploadError] = useState('');
  const [dataStats, setDataStats] = useState(null);
  const fileInputRef = useRef(null);

  // Fetch data statistics on component mount
  useEffect(() => {
    fetchDataStatistics();
  }, []);

  const fetchDataStatistics = async () => {
    try {
      const stats = await gridService.getDataStatistics();
      setDataStats(stats);
    } catch (error) {
      console.error('Error fetching data statistics:', error);
    }
  };

  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    // Check file type
    if (!file.name.endsWith('.xlsx') && !file.name.endsWith('.xls')) {
      setUploadError('Please select a valid Excel file (.xlsx or .xls)');
      return;
    }

    setIsUploading(true);
    setUploadError('');
    setUploadStatus('Uploading...');

    try {
      const result = await gridService.uploadExcel(file);
      setUploadStatus(`File uploaded successfully! Processed ${result.rows_processed} rows.`);
      
      // Refresh data statistics after successful upload
      await fetchDataStatistics();
      
      setTimeout(() => setUploadStatus(''), 5000);
      
      // Clear file input
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    } catch (error) {
      console.error('Upload error:', error);
      setUploadError(error.response?.data?.detail || 'Failed to upload file. Please try again.');
    } finally {
      setIsUploading(false);
    }
  };

  const handleDownloadSummary = async () => {
    setIsDownloading(true);
    setUploadError('');
    
    try {
      await gridService.exportData();
      setUploadStatus('Data exported successfully!');
      setTimeout(() => setUploadStatus(''), 3000);
    } catch (error) {
      console.error('Download error:', error);
      setUploadError('Failed to download data. Please try again.');
    } finally {
      setIsDownloading(false);
    }
  };

  const handleUploadClick = () => {
    fileInputRef.current?.click();
  };

  return (
    <div className="data-manager">
      <div className="data-manager-header">
        <h3>📊 Data Management</h3>
        <p className="data-manager-description">
          Upload Excel files or download system summary data
        </p>
      </div>

      <div className="data-manager-content">
        {/* Upload Section */}
        <div className="upload-section">
          <h4>📤 Upload Excel File</h4>
          <div className="upload-area">
            <input
              ref={fileInputRef}
              type="file"
              accept=".xlsx,.xls"
              onChange={handleFileUpload}
              style={{ display: 'none' }}
              disabled={isUploading}
            />
            <button 
              className="upload-button" 
              onClick={handleUploadClick}
              disabled={isUploading}
            >
              {isUploading ? (
                <>
                  <div className="upload-spinner"></div>
                  <span>Uploading...</span>
                </>
              ) : (
                <>
                  <span>📁</span>
                  <span>Choose Excel File</span>
                </>
              )}
            </button>
            <p className="upload-info">
              Supports .xlsx and .xls files
            </p>
          </div>

          {/* Upload Status */}
          {uploadStatus && (
            <div className="upload-status success">
              <span>✅</span>
              <span>{uploadStatus}</span>
            </div>
          )}

          {uploadError && (
            <div className="upload-status error">
              <span>❌</span>
              <span>{uploadError}</span>
            </div>
          )}
        </div>

        {/* Download Section */}
        <div className="download-section">
          <h4>📥 Download Summary Data</h4>
          <div className="download-options">
            <button 
              className="download-button primary"
              onClick={handleDownloadSummary}
              disabled={isDownloading}
            >
              {isDownloading ? (
                <>
                  <div className="download-spinner"></div>
                  <span>Generating...</span>
                </>
              ) : (
                <>
                  <span>📊</span>
                  <span>Download Summary (CSV)</span>
                </>
              )}
            </button>
            
            <div className="download-info">
              <p>Includes:</p>
              <ul>
                <li>Current system status</li>
                <li>Historical data (last 100 records)</li>
                <li>System health metrics</li>
                <li>Performance statistics</li>
              </ul>
            </div>
          </div>
        </div>

        {/* Data Statistics */}
        <div className="data-stats">
          <h4>📈 Data Statistics</h4>
          <div className="stats-grid">
            <div className="stat-item">
              <span className="stat-label">Total Records:</span>
              <span className="stat-value">{dataStats?.total_records || 0}</span>
            </div>
            <div className="stat-item">
              <span className="stat-label">Avg Voltage:</span>
              <span className="stat-value">{dataStats?.avg_voltage ? `${dataStats.avg_voltage.toFixed(1)}V` : 'N/A'}</span>
            </div>
            <div className="stat-item">
              <span className="stat-label">Estimated Size:</span>
              <span className="stat-value">{dataStats?.estimated_size || 'N/A'}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DataManager;
