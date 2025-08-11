-- Database schema for ML-driven Power Grid Management System
-- Created for storing grid simulation data and system metrics

CREATE TABLE IF NOT EXISTS grid_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tick INTEGER NOT NULL,
    total_voltage REAL NOT NULL,
    total_load REAL NOT NULL,
    house_count INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(tick)
);

-- Index for better query performance
CREATE INDEX IF NOT EXISTS idx_grid_data_tick ON grid_data(tick);
CREATE INDEX IF NOT EXISTS idx_grid_data_created_at ON grid_data(created_at);

-- Insert sample data if table is empty
INSERT OR IGNORE INTO grid_data (tick, total_voltage, total_load, house_count) VALUES
(1, 22000, 800, 100),
(2, 22100, 820, 102),
(3, 22200, 840, 104),
(4, 22150, 835, 103),
(5, 22300, 860, 106),
(6, 22250, 855, 105),
(7, 22400, 880, 108),
(8, 22350, 875, 107),
(9, 22500, 900, 110),
(10, 22450, 895, 109);

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
