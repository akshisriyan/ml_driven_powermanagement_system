import pandas as pd
from sklearn.svm import SVR
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import joblib
import os
import sqlite3

# Load data from SQLite (grid_data table)
backend_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'backend')
db_path = os.path.join(backend_dir, 'database.db')
conn = sqlite3.connect(db_path)
data = pd.read_sql_query("SELECT total_voltage, total_load FROM grid_data ORDER BY tick", conn)
conn.close()
X = data[['total_voltage']]
y = data['total_load']

# Split data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Scale features
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# Train SVR model
svr = SVR(kernel='rbf', C=100, epsilon=0.1)
svr.fit(X_train_scaled, y_train)

# Save model and scaler
models_dir = os.path.join(backend_dir, 'app', 'models')
os.makedirs(models_dir, exist_ok=True)
joblib.dump(svr, os.path.join(models_dir, 'svr_model.pkl'))
joblib.dump(scaler, os.path.join(models_dir, 'scaler.pkl'))

# Evaluate
print("SVR Score:", svr.score(X_test_scaled, y_test))