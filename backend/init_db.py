import sqlite3
import os

def initialize_database():
    """Initialize the SQLite database with the required schema"""
    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(script_dir, 'database.db')
    schema_path = os.path.join(script_dir, 'schema.sql')
    
    try:
        # Create database connection
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Read and execute schema file if it exists
        if os.path.exists(schema_path):
            with open(schema_path, 'r') as f:
                schema_sql = f.read()
            cursor.executescript(schema_sql)
        else:
            # Create table manually if schema file doesn't exist
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS grid_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tick INTEGER NOT NULL,
                    total_voltage REAL NOT NULL,
                    total_load REAL NOT NULL,
                    house_count INTEGER NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create indices
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_grid_data_tick ON grid_data(tick)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_grid_data_created_at ON grid_data(created_at)')
            
            # Insert sample data if table is empty
            cursor.execute('SELECT COUNT(*) FROM grid_data')
            count = cursor.fetchone()[0]
            
            if count == 0:
                sample_data = [
                    (1, 24000.0, 1000.0, 100),
                    (2, 24150.5, 1005.2, 101),
                    (3, 24200.8, 1012.8, 102),
                    (4, 24050.3, 998.5, 103),
                    (5, 24300.2, 1020.1, 104)
                ]
                cursor.executemany(
                    'INSERT INTO grid_data (tick, total_voltage, total_load, house_count) VALUES (?, ?, ?, ?)',
                    sample_data
                )
        
        conn.commit()
        conn.close()
        print(f"Database initialized successfully at {db_path}")
        
    except Exception as e:
        print(f"Error initializing database: {e}")
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    initialize_database()
