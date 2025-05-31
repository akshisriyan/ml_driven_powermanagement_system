-- Database schema for ML-Driven Power Grid Management System

-- Create grid_data table if it doesn't exist
CREATE TABLE IF NOT EXISTS grid_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tick INTEGER NOT NULL,
    total_voltage REAL NOT NULL,
    total_load REAL NOT NULL,
    house_count INTEGER NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Create index for faster queries
CREATE INDEX IF NOT EXISTS idx_grid_data_tick ON grid_data(tick);
CREATE INDEX IF NOT EXISTS idx_grid_data_created_at ON grid_data(created_at);

-- Insert sample data if table is empty
INSERT OR IGNORE INTO grid_data (tick, total_voltage, total_load, house_count)
SELECT 1, 24000.0, 1000.0, 100
WHERE NOT EXISTS (SELECT 1 FROM grid_data LIMIT 1);

-- Insert additional sample data for demonstration
INSERT OR IGNORE INTO grid_data (tick, total_voltage, total_load, house_count) VALUES
(2, 24150.5, 1005.2, 101),
(3, 24200.8, 1012.8, 102),
(4, 24050.3, 998.5, 103),
(5, 24300.2, 1020.1, 104);
