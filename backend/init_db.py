#!/usr/bin/env python3
"""
Database initialization script for ML-driven Power Grid Management System
This script creates the database schema and populates it with sample data.
"""

import sqlite3
import os
import sys

def init_database():
    """Initialize the database with schema and sample data"""
    
    # Get the directory of this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Database and schema file paths
    db_path = os.path.join(script_dir, 'database.db')
    schema_path = os.path.join(script_dir, 'schema.sql')
    
    print(f"Initializing database at: {db_path}")
    print(f"Using schema from: {schema_path}")
    
    try:
        # Create database connection
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Read and execute schema
        with open(schema_path, 'r') as schema_file:
            schema_sql = schema_file.read()
            cursor.executescript(schema_sql)
        
        # Commit changes
        conn.commit()
        
        # Verify table creation
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print(f"Created tables: {[table[0] for table in tables]}")
        
        # Check if data was inserted
        cursor.execute("SELECT COUNT(*) FROM grid_data;")
        count = cursor.fetchone()[0]
        print(f"Grid data records: {count}")
        
        conn.close()
        print("Database initialization completed successfully!")
        
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        sys.exit(1)
    except FileNotFoundError as e:
        print(f"File not found: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    init_database()
