import sqlite3
from datetime import datetime

# Connect to the database
conn = sqlite3.connect('database.db')
cursor = conn.cursor()

# Check the latest 3 records to see if environmental parameters were updated
cursor.execute("SELECT * FROM grid_data ORDER BY created_at DESC LIMIT 3")
latest_records = cursor.fetchall()
print("Latest 3 records after simulation test:")
for i, record in enumerate(latest_records):
    print(f"  Record {i+1}: {record}")

# Check specifically for the test values we sent (temp=35, humidity=80, solar=800, wind=10)
cursor.execute("SELECT COUNT(*) FROM grid_data WHERE temperature = 35.0 AND humidity = 80.0 AND solar_intensity = 800.0 AND wind_speed = 10.0")
test_count = cursor.fetchone()[0]
print(f"\nRecords with our test environmental parameters: {test_count}")

conn.close()
