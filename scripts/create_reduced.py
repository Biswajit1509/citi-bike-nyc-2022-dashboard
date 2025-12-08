"""
Create reduced sample and daily aggregated CSVs for the dashboard.
Run from project root (with your conda env active):
python scripts/create_reduced.py
"""

from pathlib import Path
import pandas as pd
import numpy as np

BASE = Path.cwd()
RAW_MERGED = BASE / "data" / "processed" / "citibike_with_weather_merged.csv"
REDUCED_DIR = BASE / "data" / "reduced"
REDUCED_DIR.mkdir(parents=True, exist_ok=True)
REDUCED_CSV = REDUCED_DIR / "reduced_data_to_plot_7.csv"
DAILY_AGG = BASE / "data" / "processed" / "daily_aggregated.csv"

if not RAW_MERGED.exists():
    raise SystemExit(f"Missing merged file: {RAW_MERGED}")

print("Loading merged CSV (this may take a moment)...")
df = pd.read_csv(RAW_MERGED, low_memory=False)

print("Columns found:", list(df.columns))

# --- find date column ---
date_cols = ['date', 'started_at', 'start_time', 'start_date', 'start_datetime']
date_col = next((c for c in date_cols if c in df.columns), None)
if date_col is None:
    raise SystemExit("No date-like column found. Please inspect your merged CSV.")

# convert to datetime
df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
df = df.dropna(subset=[date_col])  # drop rows without date

# create a normalized 'date' column (date only)
df['date'] = pd.to_datetime(df[date_col]).dt.floor('D')

# --- find temperature column (several possible names) ---
temp_candidates = ['temperature', 'temp', 'avgTemp', 'tavg', 'TAVG', 'tavg_c', 'tavg_celsius']
temp_col = next((c for c in temp_candidates if c in df.columns), None)
if temp_col:
    print("Using temperature column:", temp_col)
    df['temperature'] = pd.to_numeric(df[temp_col], errors='coerce')
else:
    print("No temperature column found in merged file. Temperature will be NaN in daily file.")
    df['temperature'] = np.nan

# --- make sure start_station_name exists for the top20 step ---
station_cols = ['start_station_name', 'from_station_name', 'start_station', 'from_station']
station_col = next((c for c in station_cols if c in df.columns), None)
if station_col:
    df.rename(columns={station_col: 'start_station_name'}, inplace=True)
else:
    # create placeholder if missing
    df['start_station_name'] = "UNKNOWN"

# --- create daily aggregated dataframe ---
print("Aggregating daily bike rides and average temperature...")
daily = (
    df.groupby('date')
      .agg(bike_rides_daily=('date', 'size'),
           temperature=('temperature', 'mean'))
      .reset_index()
)

# Save daily aggregated file
daily.to_csv(DAILY_AGG, index=False)
print("Saved daily aggregated to:", DAILY_AGG)

# --- create reduced sample with columns useful for dashboard ---
use_cols = [
    'ride_id', 'date', 'started_at', 'start_station_name', 'start_station_id',
    'end_station_name', 'end_station_id', 'start_lat', 'start_lng', 'end_lat', 'end_lng',
    'member_casual', 'temperature'
]
exist_cols = [c for c in use_cols if c in df.columns]
reduced_full = df[exist_cols].copy()

# Drop any huge extras; ensure deterministic sample
np.random.seed(32)
sample_mask = np.random.rand(len(reduced_full)) <= 0.08  # keep 8% -> about 287k if original 3.6M
reduced_sample = reduced_full[sample_mask].reset_index(drop=True)

# Save reduced sample
reduced_sample.to_csv(REDUCED_CSV, index=False)
print("Saved reduced sample to:", REDUCED_CSV)
print("Reduced sample shape:", reduced_sample.shape)
print("Daily aggregated preview:")
print(daily.head())