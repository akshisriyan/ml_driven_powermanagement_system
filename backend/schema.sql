-- Database schema for ML-driven Power Grid Management System
-- Created for storing grid simulation data and system metrics

CREATE TABLE IF NOT EXISTS grid_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tick INTEGER NOT NULL,
    total_voltage REAL NOT NULL,
    total_load REAL NOT NULL,
    temperature REAL,
    humidity REAL,
    solar_intensity REAL,
    wind_speed REAL,
    peak_hours INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(tick)
);

-- Index for better query performance
CREATE INDEX IF NOT EXISTS idx_grid_data_tick ON grid_data(tick);
CREATE INDEX IF NOT EXISTS idx_grid_data_created_at ON grid_data(created_at);

-- Insert sample data if table is empty
-- Including environmental parameters
INSERT OR IGNORE INTO grid_data (tick, total_voltage, total_load, temperature, humidity, solar_intensity, wind_speed, peak_hours) VALUES
(1, 22000, 800, 24.5, 48.0, 450.0, 4.2, 0),
(2, 22100, 820, 25.0, 49.0, 475.0, 4.5, 0),
(3, 22200, 840, 25.5, 50.0, 500.0, 4.8, 0),
(4, 22150, 835, 26.0, 51.0, 525.0, 5.0, 1),
(5, 22300, 860, 26.5, 52.0, 550.0, 5.2, 1),
(6, 22250, 855, 27.0, 53.0, 525.0, 5.0, 1),
(7, 22400, 880, 27.5, 54.0, 500.0, 4.8, 1),
(8, 22350, 875, 27.0, 53.0, 475.0, 4.5, 0),
(9, 22500, 900, 26.5, 52.0, 450.0, 4.2, 0),
(10, 22450, 895, 26.0, 51.0, 425.0, 4.0, 0);

-- Users table for authentication & authorization
CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        role TEXT NOT NULL DEFAULT 'client',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        last_login TIMESTAMP,
        is_active INTEGER DEFAULT 1
);

-- Seed an initial admin user if absent
INSERT OR IGNORE INTO users (id, username, email, password_hash, role)
VALUES (
    1,
    'admin',
    'admin@example.com',
    '$2b$12$2u9ZB2wV4dD8hYqE6N0PeOMpO3q1QXl3k9b9ZPp7AnbcW2CYwiVbS', -- password: Admin@123 (change in production)
    'admin'
);
