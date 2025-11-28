# notebooks/st_dashboard_part2.py
import streamlit as st
from pathlib import Path
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from PIL import Image

# ---------------- Paths (adjust if needed) ----------------
BASE = Path(__file__).resolve().parent.parent  # project root (one level up from notebooks/)
DATA_REDUCED = BASE / "data" / "reduced" / "reduced_data_to_plot_7.csv"
DATA_PROCESSED = BASE / "data" / "processed" / "citibike_with_weather_merged.csv"
KEPLER_HTML = BASE / "docs" / "Citibike_Aggregated_Map.html"
TOP20_CSV = BASE / "docs" / "top20.csv"
IMG_INTRO = BASE / "images" / "Divvy_Bikes.jpg"
RECS_IMG = BASE / "images" / "recs_page.png"

# ---------------- Basic page config ----------------
st.set_page_config(page_title="CitiBike NYC — Dashboard", layout="wide")
st.sidebar.title("Navigation")
page = st.sidebar.selectbox("Select an aspect of the analysis",
                            ["Intro page", "Weather & Bike Usage", "Most popular stations",
                             "Interactive map", "Recommendations"])

# ---------------- Helper: load reduced data ----------------
@st.cache_data
def load_reduced(path):
    if not path.exists():
        raise FileNotFoundError(f"Reduced CSV not found: {path}")
    df_ = pd.read_csv(path, parse_dates=["date"] if "date" in pd.read_csv(path, nrows=0).columns else None)
    # ensure datetime dtype for 'date' if there
    if "date" in df_.columns:
        df_["date"] = pd.to_datetime(df_["date"], errors="coerce")
    return df_

# Load reduced data (used for dashboard)
try:
    df = load_reduced(DATA_REDUCED)
except FileNotFoundError as e:
    st.error(str(e))
    st.stop()

# Load top20 if available (for the bar chart)
if TOP20_CSV.exists():
    top20 = pd.read_csv(TOP20_CSV)
else:
    # Compute on the fly (safe)
    df["_one"] = 1
    top20 = df.groupby("start_station_name", as_index=False)["_one"].sum().rename(columns={"_one":"count"})
    top20 = top20.nlargest(20, "count").reset_index(drop=True)

# ---------------- PAGES ----------------
if page == "Intro page":
    st.title("CitiBike NYC — Dashboard")
    st.markdown("""
    Right now, Divvy bikes run into a situation where customers complain about bikes not being available at certain times. This analysis will look at the potential reasons behind this. The dashboard is separated into 4 sections:
    
- Most popular stations
- Weather component and bike usage
- Interactive map with aggregated bike trips
- Interactive map with aggregated bike trips
- Recommendations

The dropdown menu on the left 'Aspect Selector' will take you to the different aspects of the analysis out team looked at""")
    if IMG_INTRO.exists():
        st.image(Image.open(IMG_INTRO), use_column_width=True)
    else:
        st.info("Intro image not found. To add an intro image, place `Divvy_Bikes.jpg` in the `images/` folder.")
    st.markdown("**Data**: Reduced sample of CitiBike 2022 trips combined with NOAA weather.")

# ---------------- Weather & Bike Usage ----------------
elif page == "Weather & Bike Usage":
    st.header("Daily bike rides (and temperature if available)")
    if "date" not in df.columns:
        st.warning("Reduced data has no `date` column. Dual-axis chart requires a date column.")
    else:
        # daily counts
        daily = df.groupby(df["date"].dt.date).size().reset_index(name="bike_rides_daily")
        daily["date"] = pd.to_datetime(daily["date"])
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        fig.add_trace(go.Scatter(x=daily["date"], y=daily["bike_rides_daily"], name="Daily bike rides", mode="lines"),
                      secondary_y=False)
        if "temperature" in df.columns:
            temp = df.groupby(df["date"].dt.date)["temperature"].mean().reset_index(name="temperature")
            temp["date"] = pd.to_datetime(temp["date"])
            fig.add_trace(go.Scatter(x=temp["date"], y=temp["temperature"], name="Avg Temp", mode="lines", line=dict(color="red")),
                          secondary_y=True)
            fig.update_yaxes(title_text="Temperature (°C)", secondary_y=True)
        fig.update_yaxes(title_text="Bike rides (count)", secondary_y=False)
        fig.update_layout(title="Daily Bike Rides & Temperature", height=600)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("**Interpretation:** Add 2–3 sentences describing seasonality, peaks and weather relationships.")

# ---------------- Most popular stations ----------------
elif page == "Most popular stations":
    st.header("Top 20 Start Stations")
    # optional season filter
    if "season" in df.columns:
        seasons = sorted(df["season"].dropna().unique().tolist())
        chosen = st.sidebar.multiselect("Select season(s)", options=seasons, default=seasons)
        df_filtered = df[df["season"].isin(chosen)]
    else:
        df_filtered = df
    counts = df_filtered.groupby("start_station_name").size().reset_index(name="count")
    top = counts.nlargest(20, "count").sort_values("count", ascending=True)  # ascending for horizontal bar
    fig_bar = go.Figure(go.Bar(x=top["count"], y=top["start_station_name"], orientation="h",
                               marker=dict(color=top["count"], colorscale="Blues")))
    fig_bar.update_layout(title="Top 20 Start Stations", height=700, margin=dict(l=300))
    st.plotly_chart(fig_bar, use_container_width=True)
    st.metric("Total rides (current filter)", f"{int(df_filtered.shape[0]):,}")
    st.markdown("**Interpretation:** Add a short summary about hotspots and rebalancing candidates.")

# ---------------- Interactive map ----------------
elif page == "Interactive map":
    st.header("Aggregated bike trips — Map (Kepler.gl)")
    if KEPLER_HTML.exists():
        html_data = KEPLER_HTML.read_text(encoding="utf8")
        st.components.v1.html(html_data, height=900)
        st.markdown("**Interpretation:** Use the Kepler.gl GUI to filter and inspect high-volume OD pairs.")
    else:
        st.warning(f"Kepler map HTML not found at `{KEPLER_HTML.relative_to(BASE)}`. Export it into the `docs/` folder.")

# ---------------- Recommendations ----------------
else:
    st.header("Conclusions & Recommendations")
    st.markdown("""
    **Key recommendations (examples)**:
    - Prioritize morning rebalancing at top start stations.
    - Increase bike capacity near tourist hubs during warm months.
    - Use short-term weather forecasts to trigger dynamic rebalancing.
    """)
    if RECS_IMG.exists():
        st.image(Image.open(RECS_IMG), use_column_width=True)
    else:
        st.info("Recommendation image not found. Add `recs_page.png` to the `images/` folder if desired.")
