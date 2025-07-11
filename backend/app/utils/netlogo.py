import subprocess
import os
import pandas as pd
import numpy as np
from datetime import datetime
import sqlite3

def run_netlogo_simulation():
    """
    Run NetLogo simulation. If NetLogo is not available, generate synthetic data.
    """
    
    # Try to find NetLogo installation
    possible_netlogo_paths = [
        "C:/Program Files/NetLogo 6.3.0/netlogo-headless.bat",
        "C:/Program Files/NetLogo 6.4.0/netlogo-headless.bat",
        "C:/Program Files/NetLogo 6.2.0/netlogo-headless.bat",
        "/Applications/NetLogo 6.3.0/netlogo-headless.sh",  # macOS
        "/usr/bin/netlogo-headless"  # Linux
    ]
    
    netlogo_path = None
    for path in possible_netlogo_paths:
        if os.path.exists(path):
            netlogo_path = path
            break
    
    # Get absolute paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    backend_dir = os.path.dirname(os.path.dirname(script_dir))
    project_dir = os.path.dirname(backend_dir)
    model_path = os.path.join(project_dir, "simulation", "power_grid.nlogo")
    output_path = os.path.join(project_dir, "simulation", "grid_data.csv")
    
    # If NetLogo is available and model exists, run simulation
    if netlogo_path and os.path.exists(model_path):
        try:
            cmd = [
                netlogo_path,
                "--model", model_path,
                "--table", output_path
            ]
            subprocess.run(cmd, check=True, capture_output=True, text=True)
            print("NetLogo simulation completed successfully")
            return True
        except subprocess.CalledProcessError as e:
            print(f"NetLogo simulation failed: {e.stderr}")
            # Fall back to synthetic data
            return generate_synthetic_data()
    else:
        print("NetLogo not found or model missing, generating synthetic data")
        return generate_synthetic_data()

def generate_synthetic_data():
    """
    Generate synthetic grid data for testing when NetLogo is not available.
    """
    try:
        # Get current database state
        backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        db_path = os.path.join(backend_dir, "database.db")
        
        conn = sqlite3.connect(db_path)
        
        # Get the latest tick
        cursor = conn.cursor()
        cursor.execute("SELECT MAX(tick) FROM grid_data")
        max_tick = cursor.fetchone()[0]
        next_tick = (max_tick + 1) if max_tick else 1
        
        # Generate synthetic data for next 10 ticks
        data = []
        base_voltage = 22000
        base_load = 800
        base_houses = 100
        
        for i in range(10):
            tick = next_tick + i
            
            # Add some realistic variation
            voltage_variation = np.random.normal(0, 100)
            load_variation = np.random.normal(0, 50)
            house_variation = np.random.randint(-2, 3)
            
            voltage = base_voltage + voltage_variation + (i * 25)
            load = base_load + load_variation + (i * 10)
            houses = base_houses + house_variation + (i * 2)
            
            data.append({
                'tick': tick,
                'total_voltage': round(voltage, 2),
                'total_load': round(load, 2),
                'house_count': int(houses)
            })
        
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