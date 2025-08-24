import os
import numpy as np
import pandas as pd
import joblib
from datetime import datetime
from sklearn.preprocessing import StandardScaler
from statsmodels.tsa.statespace.sarimax import SARIMAX
import warnings
warnings.filterwarnings('ignore')


class SARIMAXForecaster:
    def __init__(self, model_path=None, scaler_path=None):
        backend_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'backend')
        models_dir = os.path.join(backend_dir, 'app', 'models')
        os.makedirs(models_dir, exist_ok=True)
        if model_path is None:
            model_path = os.path.join(models_dir, 'sarimax_model.pkl')
        if scaler_path is None:
            scaler_path = os.path.join(models_dir, 'sarimax_exog_scaler.pkl')

        self.model_path = model_path
        self.scaler_path = scaler_path
        self.model = None
        self.exog_scaler = None

        if os.path.exists(self.model_path):
            try:
                self.model = joblib.load(self.model_path)
            except Exception:
                self.model = None
        if os.path.exists(self.scaler_path):
            try:
                self.exog_scaler = joblib.load(self.scaler_path)
            except Exception:
                self.exog_scaler = None

    def train(self, df, value_col='total_load', exog_cols=None, order=(1,1,1), max_iter=1):
        """Train SARIMAX on DataFrame df indexed by a datetime-like index or integer index.

        df: pandas.DataFrame containing value_col and optional exog_cols.
        """
        if exog_cols:
            exog = df[exog_cols].astype(float)
            self.exog_scaler = StandardScaler()
            exog_scaled = self.exog_scaler.fit_transform(exog)
            exog_scaled = pd.DataFrame(exog_scaled, index=exog.index, columns=exog_cols)
        else:
            exog_scaled = None

        series = df[value_col].astype(float)

        # Fit SARIMAX once (grid search is expensive on server)
        model = SARIMAX(series, exog=exog_scaled if exog_cols else None, order=order)
        fitted = model.fit(disp=False)

        # Save
        joblib.dump(fitted, self.model_path)
        if self.exog_scaler is not None:
            joblib.dump(self.exog_scaler, self.scaler_path)
        self.model = fitted
        return {
            'order': order,
            'aic': float(fitted.aic),
            'bic': float(fitted.bic)
        }

    def forecast(self, steps=10, exog_future=None):
        if self.model is None:
            raise RuntimeError('SARIMAX model not available')

        # If the fitted model includes an exogenous regression component, ensure exog_future is provided.
        # If not provided, create a zero-filled exog_future with the correct shape so forecasting can proceed.
        k_exog = 0
        try:
            k_exog = int(getattr(self.model.model, 'k_exog', 0) or 0)
        except Exception:
            try:
                k_exog = int(self.model.data.exog.shape[1])
            except Exception:
                k_exog = 0

        if k_exog > 0 and exog_future is None:
            # Determine column names if available
            cols = None
            try:
                cols = list(getattr(self.model.model, 'exog_names', None) or [])
            except Exception:
                cols = None

            if not cols or len(cols) != k_exog:
                cols = [f'exog_{i}' for i in range(k_exog)]

            exog_future = pd.DataFrame(0.0, index=range(steps), columns=cols)

        if exog_future is not None and self.exog_scaler is not None:
            # If an exog scaler exists, apply it. Accept both DataFrame or ndarray inputs.
            if not isinstance(exog_future, pd.DataFrame):
                exog_future = pd.DataFrame(exog_future)
            try:
                scaled = self.exog_scaler.transform(exog_future)
                exog_future = pd.DataFrame(scaled, index=exog_future.index, columns=exog_future.columns)
            except Exception:
                # If scaler fails, fall back to raw exog_future
                pass

        fc = self.model.get_forecast(steps=steps, exog=exog_future)
        mean = fc.predicted_mean
        ci = fc.conf_int()

        timestamps = []
        # If training index is datetime-like, generate offsets, else use integer steps
        try:
            last_index = pd.to_datetime(self.model.data.endog.index[-1])
            for i in range(steps):
                timestamps.append((last_index + pd.Timedelta(minutes=(i+1))).isoformat())
        except Exception:
            timestamps = list(range(1, steps+1))

        return {
            'timestamps': timestamps,
            'forecast': mean.tolist(),
            'lower_ci': ci.iloc[:, 0].tolist(),
            'upper_ci': ci.iloc[:, 1].tolist()
        }
