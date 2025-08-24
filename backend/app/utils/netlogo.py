import subprocess
import os
import pandas as pd
import numpy as np
from datetime import datetime
import sqlite3

def run_netlogo_simulation(env_params: dict = None):
    """
    Run NetLogo simulation. If NetLogo is not available, generate synthetic data.
    """
    
    # For now, always use synthetic data generation due to NetLogo compatibility issues
    print("Using synthetic data generation (NetLogo fallback)")
    return generate_synthetic_data(env_params)


def _ensure_zone_tables(conn):
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS zones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            category TEXT NOT NULL,
            parent_id INTEGER,
            is_active INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS zone_metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            zone_id INTEGER NOT NULL,
            tick INTEGER,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            voltage REAL,
            load REAL,
            FOREIGN KEY(zone_id) REFERENCES zones(id)
        );
        """
    )
    conn.commit()


def generate_synthetic_data(env_params: dict = None):
    """
    Generate synthetic grid data and zone metrics for testing when NetLogo is not available.
    """
    try:
        # Get current database state
        backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        db_path = os.path.join(backend_dir, "database.db")
        
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        
        # Get the latest tick
        cursor = conn.cursor()
        cursor.execute("SELECT MAX(tick) FROM grid_data")
        max_tick = cursor.fetchone()[0]
        next_tick = (max_tick + 1) if max_tick else 1
        
        # Ensure zone tables and seed defaults
        _ensure_zone_tables(conn)
        cur = conn.cursor()
        default_zones = [
            ("Faculty of Engineering", "faculty"),
            ("Faculty of Science", "faculty"),
            ("Administration", "admin"),
            ("Hostels", "hostel"),
            ("Canteen", "canteen"),
            ("Library", "library"),
        ]
        for name, cat in default_zones:
            cur.execute("INSERT OR IGNORE INTO zones(name, category) VALUES(?, ?)", (name, cat))
        conn.commit()

        # Fetch zone IDs
        cur.execute("SELECT id, name, category FROM zones")
        zones = cur.fetchall()

        # Generate synthetic data for next 10 ticks
        data = []
        base_voltage = 22000
        base_load = 800
        base_houses = 0
        
        for i in range(10):
            tick = next_tick + i
            
            # Add some realistic variation
            voltage_variation = np.random.normal(0, 100)
            load_variation = np.random.normal(0, 50)
            
            # apply environmental factors if provided
            temp = env_params.get('temperature', 25) if env_params else 25
            hum = env_params.get('humidity', 60) if env_params else 60
            light = env_params.get('lighting', 500) if env_params else 500

            # simple environmental effect on load
            env_load_factor = 1.0 + (max(0, temp - 25) * 0.002) + ((100 - min(100, hum)) * 0.0005) + (max(0, (light - 500)) * 0.00005)

            voltage = base_voltage + voltage_variation + (i * 25)
            total_load = (base_load + load_variation + (i * 10)) * env_load_factor

            data.append({
                'tick': tick,
                'total_voltage': round(voltage, 2),
                'total_load': round(total_load, 2),
                'temperature': env_params.get('temperature', 25.0) if env_params else 25.0,
                'humidity': env_params.get('humidity', 50.0) if env_params else 50.0,
                'solar_intensity': env_params.get('solar_intensity', 500.0) if env_params else 500.0,
                'wind_speed': env_params.get('wind_speed', 5.0) if env_params else 5.0,
                'peak_hours': 1 if (env_params and env_params.get('peak_hours', False)) else 0,
            })

            # Distribute load across zones by category weights
            # Assign approximate shares per category
            shares = {
                'faculty': 0.45,
                'admin': 0.08,
                'hostel': 0.28,
                'canteen': 0.10,
                'library': 0.09,
            }
            # Small noise per tick
            remaining = total_load
            zone_loads = []
            for z in zones:
                cat = z["category"]
                base_share = shares.get(cat, 0.0)
                jitter = np.random.normal(0, 0.02)
                share = max(0, base_share + jitter)
                zone_loads.append((z["id"], share))
            # Normalize shares
            s = sum(share for _, share in zone_loads) or 1.0
            zone_loads = [(zid, share / s) for zid, share in zone_loads]
            # Insert zone_metrics rows
            for zid, share in zone_loads:
                zload = max(0.0, float(total_load) * share)
                zvolt = voltage + np.random.normal(0, 50)
                cur.execute(
                    "INSERT INTO zone_metrics(zone_id, tick, voltage, load) VALUES(?, ?, ?, ?)",
                    (int(zid), tick, float(round(zvolt, 2)), float(round(zload, 2))),
                )

        # Insert data into database
        df = pd.DataFrame(data)
        df.to_sql('grid_data', conn, if_exists='append', index=False)
        conn.commit()
        conn.close()

        print(f"Generated {len(data)} synthetic data points")
        return True

    except Exception as e:
        print(f"Error generating synthetic data: {e}")
        return False


def backfill_zone_metrics_for_recent(max_rows: int = 50):
    """Distribute recent grid_data loads into zone_metrics if missing."""
    try:
        backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        db_path = os.path.join(backend_dir, "database.db")
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        _ensure_zone_tables(conn)
        cur = conn.cursor()

        # Seed defaults
        defaults = [
            ("Faculty of Engineering", "faculty"),
            ("Faculty of Science", "faculty"),
            ("Administration", "admin"),
            ("Hostels", "hostel"),
            ("Canteen", "canteen"),
            ("Library", "library"),
        ]
        for name, cat in defaults:
            cur.execute("INSERT OR IGNORE INTO zones(name, category) VALUES(?, ?)", (name, cat))
        conn.commit()

        # Load recent grid rows
        gdf = pd.read_sql_query(
            f"SELECT tick, total_voltage, total_load FROM grid_data ORDER BY tick DESC LIMIT {int(max_rows)}",
            conn,
        )
        if gdf.empty:
            conn.close()
            return False

        # Fetch zones
        cur.execute("SELECT id, category FROM zones")
        zones = cur.fetchall()
        shares = {
            'faculty': 0.45,
            'admin': 0.08,
            'hostel': 0.28,
            'canteen': 0.10,
            'library': 0.09,
        }

        inserted = 0
        for _, row in gdf.iterrows():
            tick = int(row["tick"])
            # Skip if already have any zone_metrics for this tick
            cur.execute("SELECT 1 FROM zone_metrics WHERE tick = ? LIMIT 1", (tick,))
            if cur.fetchone():
                continue

            total_load = float(row["total_load"]) if pd.notnull(row["total_load"]) else 0.0
            voltage = float(row["total_voltage"]) if pd.notnull(row["total_voltage"]) else 22000.0
            # Build normalized shares with jitter
            zshares = []
            for z in zones:
                cat = z["category"]
                base = shares.get(cat, 0.0)
                jitter = np.random.normal(0, 0.02)
                zshares.append((int(z["id"]), max(0.0, base + jitter)))
            s = sum(share for _, share in zshares) or 1.0
            zshares = [(zid, share / s) for zid, share in zshares]
            for zid, share in zshares:
                zload = max(0.0, total_load * share)
                zvolt = voltage + np.random.normal(0, 50)
                cur.execute(
                    "INSERT INTO zone_metrics(zone_id, tick, voltage, load) VALUES(?, ?, ?, ?)",
                    (zid, tick, float(round(zvolt, 2)), float(round(zload, 2))),
                )
                inserted += 1
        conn.commit()
        conn.close()
        return inserted > 0
    except Exception as e:
        print(f"Error backfilling zone metrics: {e}")
        return False