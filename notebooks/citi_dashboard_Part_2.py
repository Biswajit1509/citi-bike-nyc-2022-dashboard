# notebooks/st_dashboard_part2.py
import streamlit as st
from pathlib import Path
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from PIL import Image

# ------- paths (works when run as `streamlit run notebooks/st_dashboard_part2.py`) -------
BASE = Path(__file__).resolve().parent.parent  # project root
DATA_REDUCED = BASE / "data" / "reduced" / "reduced_data_to_plot_7.csv"
DATA_DAILY = BASE / "data" / "processed" / "daily_aggregated.csv"
KEPLER_HTML = BASE / "docs" / "Citibike_Aggregated_Map.html"
TOP20_CSV = BASE / "docs" / "top20.csv"
IMG_INTRO = BASE / "images" / "Divvy_Bikes.jpg"
RECS_IMG = BASE / "images" / "recs_page.png"

st.set_page_config(page_title="Citibike Dashboard - Part 2", layout="wide")
st.sidebar.title("Navigation")
page = st.sidebar.selectbox("Select an aspect of the analysis",
                            ["Intro page", "Weather & Bike Usage", "Most popular stations",
                             "Interactive map", "Recommendations"])

# ------- helper to load reduced data (cached) -------
@st.cache_data
def load_reduced(path):
    if not path.exists():
        raise FileNotFoundError(f"Reduced CSV not found: {path}")
    # parse date column if present
    preview = pd.read_csv(path, nrows=0)
    parse_dates = ["date"] if "date" in preview.columns else None
    df = pd.read_csv(path, parse_dates=parse_dates)
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
    return df

@st.cache_data
def load_daily(path):
    if not path.exists():
        raise FileNotFoundError(f"Daily aggregated CSV not found: {path}")
    df = pd.read_csv(path, parse_dates=["date"])
    df["date"] = pd.to_datetime(df["date"])
    return df

# Data status in sidebar
st.sidebar.markdown("### Data status")
for p in (DATA_REDUCED, DATA_DAILY, KEPLER_HTML, TOP20_CSV):
    st.sidebar.write(f"- `{p.relative_to(BASE)}` : {'✅' if p.exists() else '❌'}")

# Load reduced data (or stop)
try:
    df = load_reduced(DATA_REDUCED)
except FileNotFoundError as e:
    st.error(str(e))
    st.stop()

# Try load daily aggregated (preferred for plots)
daily_df = None
if DATA_DAILY.exists():
    try:
        daily_df = load_daily(DATA_DAILY)
    except Exception:
        daily_df = None

# If daily not found, compute from reduced sample (fallback)
if daily_df is None:
    # compute daily from reduced sample - note reduced is smaller but good for plotting locally
    if "date" not in df.columns:
        st.error("No 'date' in reduced dataset; cannot build daily aggregation.")
        st.stop()
    daily_df = df.groupby(df["date"].dt.date).size().reset_index(name="bike_rides_daily")
    daily_df["date"] = pd.to_datetime(daily_df["date"])
    # try attach temperature if exists
    if "temperature" in df.columns:
        temp = df.groupby(df["date"].dt.date)["temperature"].mean().reset_index(name="temperature")
        temp["date"] = pd.to_datetime(temp["date"])
        daily_df = daily_df.merge(temp, on="date", how="left")

# ---------------- PAGES ----------------
if page == "Intro page":
    st.title("Citibike Dashboard — Overview")
    st.markdown("""
    This interactive dashboard explores CitiBike trips in 2022 and how weather affects ridership.
    Use the sidebar to navigate to the Weather trends, Top stations, Map, and Recommendations.
    """)
    if IMG_INTRO.exists():
        st.image(Image.open(IMG_INTRO), use_column_width=True)
    else:
        st.info("Intro image not found. To add one, put Divvy_Bikes.jpg into the images/ folder.")
    st.markdown("**Data**: Reduced sample for deployment and daily aggregated CSV for plots.")

# ---------------- Weather & Bike Usage ----------------
elif page == "Weather & Bike Usage":
    st.header("Daily Bike Usage Trend (raw + 7-day avg) and Temperature")

    # Diagnostics in sidebar area
    st.sidebar.markdown(f"Daily rows: {len(daily_df)} — date range: {daily_df['date'].min().date()} to {daily_df['date'].max().date()}")

    # prepare chart data
    df_plot = daily_df.sort_values("date").copy()
    df_plot["rides_7d"] = df_plot["bike_rides_daily"].rolling(window=7, min_periods=1, center=False).mean()

    # Plotly: raw line (light), smooth 7d, and temperature on secondary y
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Scatter(x=df_plot["date"], y=df_plot["bike_rides_daily"],
                             name="Daily rides (raw)", mode="lines",
                             line=dict(width=1, color="rgb(31,119,180)"),
                             hovertemplate="%{y:,} rides<br>%{x|%Y-%m-%d}<extra></extra>"),
                  secondary_y=False)

    fig.add_trace(go.Scatter(x=df_plot["date"], y=df_plot["rides_7d"],
                             name="7-day avg (smooth)", mode="lines",
                             line=dict(width=4, color="rgb(174,199,232)"),
                             hovertemplate="%{y:,.0f} (7-day avg)<br>%{x|%Y-%m-%d}<extra></extra>"),
                  secondary_y=False)

    if "temperature" in df_plot.columns and not df_plot["temperature"].isna().all():
        fig.add_trace(go.Scatter(x=df_plot["date"], y=df_plot["temperature"],
                                 name="Avg Temp (°C)", mode="lines",
                                 line=dict(width=2, color="rgb(214,39,40)"),
                                 hovertemplate="%{y:.1f} °C<br>%{x|%Y-%m-%d}<extra></extra>"),
                      secondary_y=True)
        fig.update_yaxes(title_text="Temperature (°C)", secondary_y=True)

    fig.update_yaxes(title_text="Bike rides (count)", secondary_y=False)
    fig.update_layout(title="Daily Bike Rides & Temperature", height=600,
                      legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("**Interpretation:** Add 2–3 sentences about trends, peaks and weather relationships.")

# ---------------- Most popular stations ----------------
elif page == "Most popular stations":
    st.header("Top 20 Start Stations")
    if "start_station_name" not in df.columns:
        st.warning("Column 'start_station_name' not present in reduced data.")
    else:
        # optional season filter (if season exists)
        if "season" in df.columns:
            seasons = sorted(df["season"].dropna().unique().tolist())
            chosen = st.sidebar.multiselect("Select season(s)", options=seasons, default=seasons)
            df_filtered = df[df["season"].isin(chosen)]
        else:
            df_filtered = df

        counts = df_filtered.groupby("start_station_name").size().reset_index(name="count")
        top = counts.nlargest(20, "count").sort_values("count", ascending=True)
        fig_bar = go.Figure(go.Bar(x=top["count"], y=top["start_station_name"], orientation="h",
                                   marker=dict(color=top["count"], colorscale="Blues")))
        fig_bar.update_layout(title="Top 20 Start Stations", height=700, margin=dict(l=300))
        st.plotly_chart(fig_bar, use_container_width=True)
        st.metric("Total rides (current filter)", f"{int(df_filtered.shape[0]):,}")
        st.markdown("**Interpretation:** Add short summary about hotspots and rebalancing candidates.")

# ---------------- Interactive map ----------------
elif page == "Interactive map":
    st.header("Aggregated bike trips — Map (Kepler.gl)")
    if KEPLER_HTML.exists():
        html_data = KEPLER_HTML.read_text(encoding="utf8")
        st.components.v1.html(html_data, height=900)
        st.markdown("**Interpretation:** Use Kepler filters to inspect high-volume OD pairs.")
    else:
        st.warning(f"Kepler map HTML not found at `{KEPLER_HTML.relative_to(BASE)}` — place the exported file there.")

# ---------------- Recommendations ----------------
else:
    st.header("Conclusions & Recommendations")
    st.markdown("""
    **Key recommendations (examples)**:
    - Prioritize morning rebalancing at major start stations.
    - Increase bike capacity near tourist hubs during warm months.
    - Use short-term weather forecasts to trigger dynamic rebalancing.
    """)
    if RECS_IMG.exists():
        st.image(Image.open(RECS_IMG), use_column_width=True)