# scripts/test_daily.py
from pathlib import Path
import pandas as pd

p = Path("data/reduced/reduced_data_to_plot_7.csv")
if not p.exists():
    raise SystemExit("Reduced CSV not found: " + str(p))

df = pd.read_csv(p, parse_dates=["date"])
print(df.head(8))
print(df.columns.tolist())
print(df.dtypes)
print("min/max date:", df['date'].min(), df['date'].max())
print("bike_rides_daily stats:", df['bike_rides_daily'].describe())