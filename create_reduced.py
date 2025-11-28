# scripts/create_reduced.py
import pandas as pd
import numpy as np
from pathlib import Path

# Paths - update if your data path differs
SRC = Path("data/processed/citibike_with_weather_merged.csv")
OUT_DIR = Path("data/reduced")
OUT_DIR.mkdir(parents=True, exist_ok=True)
OUT = OUT_DIR / "reduced_data_to_plot_7.csv"

print("Reading (may take a while)...", SRC)
df = pd.read_csv(SRC, low_memory=False, parse_dates=['date'])
print(df.columns)
print(df.head())
print(df.shape)
# df_daily = df.groupby("date")[["ride_id"]].count().reset_index().rename(columns={"ride_id":"bike_rides_daily"})
# print(df_daily.head())
# print(df_daily.shape)