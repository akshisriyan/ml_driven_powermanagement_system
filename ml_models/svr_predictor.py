import numpy as np
import pandas as pd
import os
from datetime import datetime
import warnings
from sklearn.svm import SVR
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_percentage_error
from sklearn.model_selection import GridSearchCV
import joblib
warnings.filterwarnings('ignore')


class SVRPredictor:
    def __init__(self, model_path=None, scaler_path=None):
        """
        Initialize SVR Predictor
        """
        # Resolve default paths to backend/app/models within repo
        repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        backend_models_dir = os.path.join(repo_root, 'backend', 'app', 'models')
        os.makedirs(backend_models_dir, exist_ok=True)

        if model_path is None:
            model_path = os.path.join(backend_models_dir, 'svr_model.pkl')
        if scaler_path is None:
            scaler_path = os.path.join(backend_models_dir, 'scaler.pkl')

        self.model_path = model_path
        self.scaler_path = scaler_path
        self.model = None
        self.scaler = None
        self.feature_names = ['lag1_peak_kwh', 'lag2_peak_kwh', 'lag3_peak_kwh', 'day_kwh', 'off_peak_kwh', 'max_demand_kva', 'temperature', 'humidity', 'lighting']
        self.target_col = 'Peak kWh (18.30-22.30)'
        self.day_kwh_col = 'Day kWh (5.30-18.30)'
        self.off_peak_kwh_col = 'Off-peak kWh (22.30-05.30)'
        self.max_demand_col = 'Maximum Demand Charge per month kVA'
        self.timestamp_col = 'Month'
        self.train_data = None
        self.test_data = None
        self.test_data_full = None

        if os.path.exists(self.model_path) and os.path.exists(self.scaler_path):
            try:
                self.load_models()
            except Exception:
                # don't block if load fails here
                pass

    def load_models(self):
        """Load the pre-trained SVR model and scaler"""
        self.model = joblib.load(self.model_path)
        self.scaler = joblib.load(self.scaler_path)
        return True

    def clean_data(self, df, timestamp_col='Month', target_col='Peak kWh (18.30-22.30)',
                   day_kwh_col='Day kWh (5.30-18.30)', off_peak_kwh_col='Off-peak kWh (22.30-05.30)',
                   max_demand_col='Maximum Demand Charge per month kVA'):
        try:
            # Basic column normalization (strip whitespace and newlines)
            df.columns = [str(c).strip() for c in df.columns]

            # Ensure required columns exist
            required = [timestamp_col, target_col, day_kwh_col, off_peak_kwh_col, max_demand_col]
            missing = [c for c in required if c not in df.columns]
            if missing:
                raise ValueError(f"Missing required columns: {missing}")

            # Drop duplicates and rows with missing critical fields
            df = df.drop_duplicates()
            df = df.dropna(subset=[timestamp_col, target_col, day_kwh_col, off_peak_kwh_col, max_demand_col])

            # Convert timestamp
            if not pd.api.types.is_datetime64_any_dtype(df[timestamp_col]):
                df[timestamp_col] = pd.to_datetime(df[timestamp_col], errors='coerce')
                if df[timestamp_col].isna().any():
                    raise ValueError(f"Some values in {timestamp_col} cannot be parsed as datetime")

            df = df.set_index(timestamp_col)

            # Ensure numeric
            for c in [target_col, day_kwh_col, off_peak_kwh_col, max_demand_col]:
                df[c] = pd.to_numeric(df[c], errors='coerce')
            df = df.dropna(subset=[target_col, day_kwh_col, off_peak_kwh_col, max_demand_col])

            return df, timestamp_col, target_col, day_kwh_col, off_peak_kwh_col, max_demand_col
        except Exception as e:
            print('clean_data error:', e)
            return None, timestamp_col, target_col, day_kwh_col, off_peak_kwh_col, max_demand_col

    def prepare_features(self, df, target_col, day_kwh_col, off_peak_kwh_col, max_demand_col):
        try:
            df['lag1_peak_kwh'] = df[target_col].shift(1)
            df['lag2_peak_kwh'] = df[target_col].shift(2)
            df['lag3_peak_kwh'] = df[target_col].shift(3)

            df['day_kwh'] = df[day_kwh_col]
            df['off_peak_kwh'] = df[off_peak_kwh_col]
            df['max_demand_kva'] = df[max_demand_col]

            if 'temperature' not in df.columns:
                df['temperature'] = np.random.uniform(20, 35, len(df))
            if 'humidity' not in df.columns:
                df['humidity'] = np.random.uniform(50, 90, len(df))
            if 'lighting' not in df.columns:
                df['lighting'] = np.random.uniform(100, 1000, len(df))

            feature_cols = self.feature_names
            df = df.dropna(subset=feature_cols + [target_col])

            X = df[feature_cols]
            y = df[target_col]
            return X, y, df
        except Exception as e:
            print('prepare_features error:', e)
            return None, None, None

    def train_model(self, data_path, timestamp_col='Month', target_col='Peak kWh (18.30-22.30)',
                    day_kwh_col='Day kWh (5.30-18.30)', off_peak_kwh_col='Off-peak kWh (22.30-05.30)',
                    max_demand_col='Maximum Demand Charge per month kVA', train_split=0.8):
        try:
            if data_path.endswith('.csv'):
                df = pd.read_csv(data_path)
            elif data_path.endswith(('.xlsx', '.xls')):
                df = pd.read_excel(data_path)
            else:
                raise ValueError('Unsupported file format')

            df, timestamp_col, target_col, day_kwh_col, off_peak_kwh_col, max_demand_col = self.clean_data(
                df, timestamp_col, target_col, day_kwh_col, off_peak_kwh_col, max_demand_col)
            if df is None:
                return None

            X, y, df_full = self.prepare_features(df, target_col, day_kwh_col, off_peak_kwh_col, max_demand_col)
            if X is None or y is None:
                return None

            train_size = int(len(X) * train_split)
            X_train = X.iloc[:train_size]
            X_test = X.iloc[train_size:]
            y_train = y.iloc[:train_size]
            y_test = y.iloc[train_size:]

            self.scaler = StandardScaler()
            X_train_scaled = self.scaler.fit_transform(X_train)
            X_test_scaled = self.scaler.transform(X_test)

            param_grid = {
                'C': [100, 1000, 5000],
                'gamma': [0.001, 0.01, 0.1],
                'epsilon': [0.01, 0.1, 0.5]
            }
            base_model = SVR(kernel='rbf')
            grid_search = GridSearchCV(base_model, param_grid, cv=3, scoring='neg_mean_absolute_percentage_error', n_jobs=-1)
            grid_search.fit(X_train_scaled, y_train)
            self.model = grid_search.best_estimator_

            joblib.dump(self.model, self.model_path)
            joblib.dump(self.scaler, self.scaler_path)

            # Evaluate
            if len(X_test) > 0:
                y_pred = self.model.predict(X_test_scaled)
                mse = mean_squared_error(y_test, y_pred)
                rmse = np.sqrt(mse)
                r2 = r2_score(y_test, y_pred)
                mape = mean_absolute_percentage_error(y_test, y_pred) * 100
                accuracy = 100 - mape
                return {'mse': mse, 'rmse': rmse, 'r2': r2, 'accuracy': accuracy, 'best_params': grid_search.best_params_}
            return None
        except Exception as e:
            print('train_model error:', e)
            return None

    def predict_load(self, input_data):
        try:
            if self.model is None or self.scaler is None:
                raise ValueError('Model or scaler not initialized')
            input_data = np.array([input_data])
            if np.any(np.isnan(input_data)):
                print('Input contains NaN')
                return None
            scaled = self.scaler.transform(input_data)
            pred = self.model.predict(scaled)
            return float(pred[0])
        except Exception as e:
            print('predict_load error:', e)
            return None

    def predict_batch(self, data):
        try:
            if isinstance(data, list):
                data = np.array(data)
            scaled = self.scaler.transform(data)
            preds = self.model.predict(scaled)
            return preds.tolist()
        except Exception as e:
            print('predict_batch error:', e)
            return None

    def get_model_info(self):
        if self.model and self.scaler:
            return {'model_type': 'SVR', 'kernel': self.model.kernel, 'C': self.model.C, 'gamma': self.model.gamma, 'epsilon': self.model.epsilon, 'n_support': self.model.n_support_, 'features': self.feature_names}
        return None


if __name__ == '__main__':
    print('SVR predictor module loaded. Use SVRPredictor.train_model(data_path) to train or instantiate and call predict_load.')
