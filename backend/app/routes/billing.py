from fastapi import APIRouter, HTTPException, UploadFile, File
from fastapi.responses import JSONResponse
import pandas as pd
import sqlite3
import os
import io
import re
from datetime import datetime
import numpy as np

router = APIRouter(prefix="/billing", tags=["billing"])


def get_database_path():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    backend_dir = os.path.dirname(os.path.dirname(current_dir))
    return os.path.join(backend_dir, 'database.db')


def ensure_billing_table(conn: sqlite3.Connection):
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS billing_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            month TEXT NOT NULL,
            peak_kwh REAL,
            day_kwh REAL,
            offpeak_kwh REAL,
            max_demand_kva REAL,
            peak_rate REAL,
            day_rate REAL,
            offpeak_rate REAL,
            max_demand_rate REAL,
            cost_peak REAL,
            cost_day REAL,
            cost_offpeak REAL,
            cost_demand REAL,
            fixed_charge REAL,
            total_before_tax REAL,
            ssc_levy REAL,
            total_after_tax REAL,
            interest REAL,
            interest_sec_deposit REAL,
            tariff_adjustment REAL,
            sscl_adjustment REAL,
            total_payable REAL,
            change_amount REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(month)
        )
        """
    )


def normalize(name: str) -> str:
    # Normalize header text: lowercase, collapse spaces, remove common punctuation
    text = (
        str(name)
        .lower()
        .replace("\n", " ")
        .replace("\u00a0", " ")
        .replace("\xa0", " ")
    )
    # Remove redundant punctuation while keeping signs/decimals in units
    text = re.sub(r"[\t\r]+", " ", text)
    text = re.sub(r"[\(\)\[\]]", " ", text)
    text = re.sub(r"[\.:]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


COL_MAP = {
    # kWh columns
    "peak kwh (18.30-22.30)": "peak_kwh",
    "day kwh (5.30-18.30)": "day_kwh",
    "off-peak kwh (22.30-05.30)": "offpeak_kwh",
    # max demand
    "maximum demand charge per month kva": "max_demand_kva",
    # rates
    "peak rate per kwh rs.": "peak_rate",
    "day rate per kwh rs.": "day_rate",
    "off-peak rate per kwh rs.": "offpeak_rate",
    "max demand rate per kva rs.": "max_demand_rate",
    # costs
    "cost peak rs.": "cost_peak",
    "cost day rs.": "cost_day",
    "cost off-peak rs.": "cost_offpeak",
    "cost demand charge rs.": "cost_demand",
    # fixed & totals
    "fixed charge": "fixed_charge",
    # totals (typo + correct spellings)
    "total elecricity bill before tax": "total_before_tax",
    "total electricity bill before tax": "total_before_tax",
    "ssc levy": "ssc_levy",
    "total elecricity bill after tax": "total_after_tax",
    "total electricity bill after tax": "total_after_tax",
    "interest": "interest",
    "interest. for sec. deposit": "interest_sec_deposit",
    "tariff adjustment": "tariff_adjustment",
    "sscl for adjust. due to tariff change": "sscl_adjustment",
    "total amount payble": "total_payable",
    "total amount payable": "total_payable",
    # misc
    "change": "change_amount",
}


def detect_month_column(df: pd.DataFrame) -> str | None:
    """Detect the month column using name hints and data heuristics."""
    # 1) Exact/common header names
    name_hints = [
        "month",
        "billing month",
        "period",
        "month name",
    ]
    for cand in name_hints:
        if cand in df.columns:
            return cand

    # 2) Any header containing the substring 'month'
    for col in df.columns:
        if "month" in str(col):
            return col

    # 3) Heuristic: pick the column where the majority of non-null sample values parse as dates
    best_col = None
    best_score = 0
    for col in df.columns:
        s = df[col].dropna().astype(str).head(50)
        if s.empty:
            continue
        parsed = pd.to_datetime(s, errors="coerce", dayfirst=True)
        score = parsed.notna().mean()  # fraction parsable
        if score > best_score:
            best_score = score
            best_col = col
    if best_col is not None and best_score >= 0.5:
        return best_col
    return None


def read_excel_detect_header(contents: bytes) -> pd.DataFrame:
    """Read Excel and detect the header row that contains 'month'.
    Returns a DataFrame with the detected header applied and data rows below it.
    """
    raw = pd.read_excel(io.BytesIO(contents), header=None, dtype=object)
    header_idx = None
    scan_rows = min(15, len(raw))
    for i in range(scan_rows):
        row_vals = [normalize(v) for v in list(raw.iloc[i].astype(str).fillna(""))]
        # look for exact 'month' or any cell containing 'month'
        if any(v == "month" or "month" in v for v in row_vals):
            header_idx = i
            break
    if header_idx is None:
        # fallback to first row as header
        header_idx = 0
    cols = [normalize(v) for v in list(raw.iloc[header_idx].astype(str))]
    df = raw.iloc[header_idx + 1 :].reset_index(drop=True)
    df.columns = cols
    # drop columns that are completely empty
    df = df.loc[:, ~(df.isna().all())]
    return df


def to_float(val):
    """Parse numbers like 1,234,567 or (1,234) or '-' into floats.
    Handles a scalar, list/tuple, numpy array, or pandas Series by taking the
    first non-null parsed value. Returns None when not parsable.
    """
    # If we got a vector-like (Series/array/list), try each element
    if hasattr(val, "tolist") and not isinstance(val, (bytes, str)):
        try:
            seq = val.tolist()
        except Exception:
            seq = None
        if isinstance(seq, list):
            for item in seq:
                parsed = to_float(item)
                if parsed is not None:
                    return parsed
            return None
    if isinstance(val, (list, tuple)):
        for item in val:
            parsed = to_float(item)
            if parsed is not None:
                return parsed
        return None

    # Now handle a scalar
    try:
        if pd.isna(val):
            return None
    except Exception:
        pass
    if isinstance(val, (int, float)):
        try:
            return float(val)
        except Exception:
            return None
    s = str(val).strip()
    if s == "":
        return None
    # Treat '-' or '—' or '–' as zero
    if s in {"-", "—", "–"}:
        return 0.0
    # Handle percentage values like '10%'
    perc = False
    if s.endswith('%'):
        perc = True
        s = s[:-1]
    neg = False
    if s.startswith("(") and s.endswith(")"):
        neg = True
        s = s[1:-1]
    # Remove thousand separators and spaces
    s = s.replace(",", "").replace(" ", "")
    try:
        v = float(s)
        if perc:
            v = v / 100.0
        return -v if neg else v
    except Exception:
        return None


@router.post("/upload-excel")
async def upload_billing_excel(file: UploadFile = File(...)):
    if not file.filename.endswith((".xlsx", ".xls")):
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload an Excel file.")

    contents = await file.read()
    try:
        df = read_excel_detect_header(contents)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to read Excel: {e}")

    # Normalize columns
    original_columns = list(df.columns)

    # Find month column (flexible name or heuristic)
    month_col = detect_month_column(df)
    if not month_col:
        raise HTTPException(
            status_code=400,
            detail=f"Month column not found. Please include a 'Month' column. Detected columns: {', '.join(original_columns)}")

    # Map columns to db fields
    # Normalize the mapping keys the same way as the DataFrame columns
    NORM_COL_MAP = {normalize(k): v for k, v in COL_MAP.items()}
    mapped_cols = {}
    for col in df.columns:
        if col == month_col:
            continue
        if col in NORM_COL_MAP:
            mapped_cols[col] = NORM_COL_MAP[col]

    # Build records
    records = []
    for _, row in df.iterrows():
        month_raw = str(row.get(month_col, '')).strip()
        # Skip any repeated header rows or empty rows
        if normalize(month_raw) == "month":
            continue
        if not month_raw:
            continue
        # Normalize month to YYYY-MM if parsable
        month_norm = month_raw
        try:
            dt = pd.to_datetime(month_raw, errors='coerce')
            if pd.notnull(dt):
                month_norm = dt.strftime('%Y-%m')
        except Exception:
            pass

        rec = { 'month': month_norm }
        # Assign mapped values as floats when possible
        for src, dst in mapped_cols.items():
            val = row.get(src, None)
            rec[dst] = to_float(val)

        # Compute derived costs if missing
        def safe(v):
            return v if isinstance(v, (int, float)) else None

        if rec.get('cost_peak') is None and safe(rec.get('peak_kwh')) is not None and safe(rec.get('peak_rate')) is not None:
            rec['cost_peak'] = rec['peak_kwh'] * rec['peak_rate']
        if rec.get('cost_day') is None and safe(rec.get('day_kwh')) is not None and safe(rec.get('day_rate')) is not None:
            rec['cost_day'] = rec['day_kwh'] * rec['day_rate']
        if rec.get('cost_offpeak') is None and safe(rec.get('offpeak_kwh')) is not None and safe(rec.get('offpeak_rate')) is not None:
            rec['cost_offpeak'] = rec['offpeak_kwh'] * rec['offpeak_rate']
        if rec.get('cost_demand') is None and safe(rec.get('max_demand_kva')) is not None and safe(rec.get('max_demand_rate')) is not None:
            rec['cost_demand'] = rec['max_demand_kva'] * rec['max_demand_rate']

        # Totals
        if rec.get('total_before_tax') is None:
            subtotal = sum(filter(None, [rec.get('cost_peak'), rec.get('cost_day'), rec.get('cost_offpeak'), rec.get('cost_demand'), rec.get('fixed_charge')]))
            rec['total_before_tax'] = subtotal if subtotal is not None else None

        if rec.get('total_after_tax') is None:
            total_after = rec.get('total_before_tax')
            for extra in ['ssc_levy', 'interest', 'interest_sec_deposit', 'tariff_adjustment', 'sscl_adjustment']:
                v = rec.get(extra)
                if isinstance(v, (int, float)):
                    total_after = (total_after or 0) + v
            rec['total_after_tax'] = total_after

        if rec.get('total_payable') is None:
            rec['total_payable'] = rec.get('total_after_tax')

        records.append(rec)

    if not records:
        raise HTTPException(status_code=400, detail="No valid rows found in the uploaded file.")

    # Insert into DB
    with sqlite3.connect(get_database_path()) as conn:
        ensure_billing_table(conn)
        df_out = pd.DataFrame(records)
        # Upsert by month
        months = tuple(df_out['month'].unique().tolist())
        if len(months) == 1:
            conn.execute("DELETE FROM billing_records WHERE month = ?", (months[0],))
        else:
            qmarks = ",".join(["?"] * len(months))
            conn.execute(f"DELETE FROM billing_records WHERE month IN ({qmarks})", months)
        df_out.to_sql('billing_records', conn, if_exists='append', index=False)

    return {"message": "Billing file processed", "rows": len(records), "columns": original_columns}


@router.get("/summary")
def billing_summary():
    with sqlite3.connect(get_database_path()) as conn:
        ensure_billing_table(conn)
        df = pd.read_sql_query("SELECT * FROM billing_records ORDER BY month", conn)
        if df.empty:
            return {
                "total_months": 0,
                "totals": {},
                "latest": None,
                "series": []
            }
        numeric_like = [
            'peak_kwh','day_kwh','offpeak_kwh','max_demand_kva',
            'peak_rate','day_rate','offpeak_rate','max_demand_rate',
            'cost_peak','cost_day','cost_offpeak','cost_demand',
            'fixed_charge','total_before_tax','ssc_levy','total_after_tax',
            'interest','interest_sec_deposit','tariff_adjustment','sscl_adjustment',
            'total_payable','change_amount'
        ]
        numeric_cols = [c for c in numeric_like if c in df.columns]
        for c in numeric_cols:
            df[c] = pd.to_numeric(df[c], errors='coerce')
        totals_raw = df[numeric_cols].sum(skipna=True).to_dict()
        totals = {k: (None if (v is None or (isinstance(v, float) and np.isnan(v))) else float(v)) for k, v in totals_raw.items()}

        latest_raw = df.iloc[-1].to_dict()
        latest = {k: (None if (isinstance(v, float) and np.isnan(v)) else v) for k, v in latest_raw.items()}

        series_cols = [c for c in ['month','peak_kwh','day_kwh','offpeak_kwh','total_payable'] if c in df.columns]
        series_df = df[series_cols].copy()
        for c in ['peak_kwh','day_kwh','offpeak_kwh','total_payable']:
            if c in series_df.columns:
                series_df[c] = pd.to_numeric(series_df[c], errors='coerce').fillna(0)
        series = series_df.to_dict(orient='records')
        return {
            "total_months": int(len(df)),
            "totals": totals,
            "latest": latest,
            "series": series
        }


@router.get("/monthly")
def billing_monthly():
    with sqlite3.connect(get_database_path()) as conn:
        ensure_billing_table(conn)
        df = pd.read_sql_query("SELECT * FROM billing_records ORDER BY month", conn)
        numeric_like = [
            'peak_kwh','day_kwh','offpeak_kwh','max_demand_kva',
            'peak_rate','day_rate','offpeak_rate','max_demand_rate',
            'cost_peak','cost_day','cost_offpeak','cost_demand',
            'fixed_charge','total_before_tax','ssc_levy','total_after_tax',
            'interest','interest_sec_deposit','tariff_adjustment','sscl_adjustment',
            'total_payable','change_amount'
        ]
        for c in numeric_like:
            if c in df.columns:
                df[c] = pd.to_numeric(df[c], errors='coerce')
        # Convert to object dtype so None can replace NaN reliably
        df = df.astype(object)
        df = df.where(pd.notna(df), None)
        return df.to_dict(orient='records')
