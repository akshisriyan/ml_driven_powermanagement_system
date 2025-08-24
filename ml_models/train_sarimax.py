import os
import sqlite3
import pandas as pd
from ml_models.sarimax_forecaster import SARIMAXForecaster


def load_grid_data(db_path):
    conn = sqlite3.connect(db_path)
    df = pd.read_sql_query('select * from grid_data order by tick asc', conn)
    conn.close()
    if 'created_at' in df.columns:
        df['created_at'] = pd.to_datetime(df['created_at'], errors='coerce')
        df = df.set_index('created_at')
    elif 'tick' in df.columns:
        df = df.set_index('tick')
    return df


if __name__ == '__main__':
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    db_path = os.path.join(repo_root, 'backend', 'database.db')

    df = load_grid_data(db_path)
    if df.empty:
        print('No grid_data found in DB, aborting SARIMAX training.')
        exit(1)

    # Prepare exogenous variables if available (exclude house_count; use environmental vars or voltage)
    exog_cols = []
    for c in ['total_voltage']:
        if c in df.columns and c != 'total_load':
            exog_cols.append(c)

    forecaster = SARIMAXForecaster()
    print('Training SARIMAX on', len(df), 'rows')
    info = forecaster.train(df, value_col='total_load', exog_cols=exog_cols or None, order=(1,1,1))
    print('SARIMAX training complete:', info)
