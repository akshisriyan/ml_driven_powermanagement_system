import sqlite3
from datetime import datetime

# Connect to the database
conn = sqlite3.connect('database.db')
cursor = conn.cursor()

# Check the grid_data table structure
cursor.execute("PRAGMA table_info(grid_data)")
columns = cursor.fetchall()
print("Grid data table structure:")
for col in columns:
    print(f"  {col[1]} ({col[2]})")
print()

# Check the total number of rows
cursor.execute("SELECT COUNT(*) FROM grid_data")
count = cursor.fetchone()[0]
print(f"Total grid_data rows: {count}")

# Check the latest 5 records
cursor.execute("SELECT * FROM grid_data ORDER BY created_at DESC LIMIT 5")
latest_records = cursor.fetchall()
print("\nLatest 5 records:")
for i, record in enumerate(latest_records):
    print(f"  Record {i+1}: {record}")

# Check the date range of the data
cursor.execute("SELECT MIN(created_at), MAX(created_at) FROM grid_data")
date_range = cursor.fetchone()
print(f"\nData date range: {date_range[0]} to {date_range[1]}")

# Check if there's any recent data (within last hour)
cursor.execute("SELECT COUNT(*) FROM grid_data WHERE created_at > datetime('now', '-1 hour')")
recent_count = cursor.fetchone()[0]
print(f"Records from last hour: {recent_count}")

conn.close()
