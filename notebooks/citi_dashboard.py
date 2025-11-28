# citi_dashboard.py  (PUT IN PROJECT ROOT: C:/Users/Biswajit/citi-bike-nyc-2022-dashboard/citi_dashboard.py)
import streamlit as st
import pandas as pd
from pathlib import Path
from plotly.subplots import make_subplots
import plotly.graph_objects as go

st.set_page_config(page_title="CitiBike NYC 2022 Dashboard", layout="wide")
st.title("CitiBike NYC 2022 — Trip counts & Weather")
st.markdown("Interactive dashboard showing trip counts and (if available) temperature. Map exported from Kepler.gl is embedded below.")

# ---------- Paths ----------
BASE = Path(__file__).resolve().parent
MERGED_CSV = BASE / "data" / "processed" / "citibike_with_weather_merged.csv"
TOP20_CSV = BASE / "docs" / "top20.csv"
KEPLER_HTML = BASE / "docs" / "Citibike_Aggregated_Map.html"

# ---------- Load data with caching ----------
@st.cache_data
def load_merged(path):
    return pd.read_csv(path, low_memory=False)

st.sidebar.header("Data & Controls")
st.sidebar.write("Loading data (cached).")
try:
    df = load_merged(MERGED_CSV)
    st.sidebar.success("Loaded merged dataset.")
except Exception as e:
    st.sidebar.error(f"Failed to read merged CSV: {e}")
    st.stop()

# --- Prepare top20 if exists
if TOP20_CSV.exists():
    top20 = pd.read_csv(TOP20_CSV)
else:
    df['_one'] = 1
    top20 = df.groupby('start_station_name', as_index=False).agg(count=('_one','sum')).nlargest(20,'count')
    (BASE / "docs").mkdir(exist_ok=True, parents=True)
    top20.to_csv(TOP20_CSV, index=False)

# --- Show bar chart (plotly)
st.subheader("Top 20 Start Stations")
fig_bar = go.Figure(go.Bar(
    x=top20['count'][::-1],
    y=top20['start_station_name'][::-1],
    orientation='h',
    marker=dict(color=top20['count'], colorscale='Blues'),
    hovertemplate='%{y}<br>Trips: %{x}<extra></extra>'
))
fig_bar.update_layout(title='Top 20 Start Stations (NYC 2022)', xaxis_title='Trips', height=650, margin=dict(l=300))
st.plotly_chart(fig_bar, use_container_width=True)

# --- Prepare daily_df
if 'date' not in df.columns:
    if 'started_at' in df.columns:
        df['date'] = pd.to_datetime(df['started_at']).dt.date
    else:
        st.warning("No 'date' or 'started_at' columns; cannot build daily aggregations.")
        st.stop()
df['date'] = pd.to_datetime(df['date'])
if 'ride_id' in df.columns:
    daily_df = df.groupby('date').agg(bike_rides_daily=('ride_id','count')).reset_index()
else:
    daily_df = df.groupby('date').size().reset_index(name='bike_rides_daily')

# attempt to detect temperature column from NOAA merge
if 'datatype' in df.columns and 'value' in df.columns:
    temp_df = df[df['datatype'].str.contains('TAVG', na=False)][['date','value']].copy()
    if not temp_df.empty:
        temp_daily = temp_df.groupby('date').agg(temperature=('value','mean')).reset_index()
        daily_df = daily_df.merge(temp_daily, on='date', how='left')

# --- Dual-axis plot
st.subheader("Daily Bike Rides and Temperature (if available)")
fig = make_subplots(specs=[[{"secondary_y": True}]])
fig.add_trace(go.Scatter(x=daily_df['date'], y=daily_df['bike_rides_daily'], name='Daily Bike Rides', mode='lines'), secondary_y=False)
if 'temperature' in daily_df.columns and daily_df['temperature'].notna().any():
    fig.add_trace(go.Scatter(x=daily_df['date'], y=daily_df['temperature'], name='Avg Temp', mode='lines'), secondary_y=True)
else:
    st.info("No temperature data available in merged CSV; only bike rides plotted.")

fig.update_yaxes(title_text="Bike rides (count)", secondary_y=False)
fig.update_yaxes(title_text="Temperature", secondary_y=True)
fig.update_layout(title='Daily Bike Rides and Temperature', height=600)
st.plotly_chart(fig, use_container_width=True)

# --- Embed kepler map (safe)
st.subheader("Aggregated trips map (Kepler.gl)")
if KEPLER_HTML.exists():
    # Option: embed or show link. If HTML is heavy, both shown: link + small iframe preview.
    st.markdown("Interactive map is available — open in a new tab (recommended) or view inline (may be slow).")
    st.markdown(f"[Open interactive map in a new tab]({KEPLER_HTML.name})")
    try:
        html_data = KEPLER_HTML.read_text()
        st.components.v1.html(html_data, height=700, scrolling=True)
    except Exception as e:
        st.warning(f"Could not embed HTML in page (size or scripts). Open the file directly: {KEPLER_HTML}")
else:
    st.info("Kepler HTML map not found in docs. Place the Citibike_Aggregated_Map.html file in docs/")

st.markdown("---")
st.markdown("**Notes:** Data files are large and therefore not pushed to remote as instructed. See README for details.")