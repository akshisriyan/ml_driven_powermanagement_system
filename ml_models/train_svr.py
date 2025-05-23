import pandas as pd
from sklearn.svm import SVR
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import joblib

# Load data from NetLogo simulation
data = pd.read_csv('../simulation/grid_data.csv')
X = data[['voltage', 'house_count']]
y = data['load']

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
joblib.dump(svr, '../backend/app/models/svr_model.pkl')
joblib.dump(scaler, '../backend/app/models/scaler.pkl')

# Evaluate
print("SVR Score:", svr.score(X_test_scaled, y_test))