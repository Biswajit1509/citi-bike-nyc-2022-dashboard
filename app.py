# ----- IMPORTS -----
import streamlit as st
import pandas as pd
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import streamlit.components.v1 as components

# ----- PAGE CONFIG -----
st.set_page_config(page_title="Citi Bike 2022 – NYC Dashboard", layout="wide")

KEPLER_HTML = "docs/Citibike_Aggregated_Map.html"


# ----- DATA LOADING -----
@st.cache_data
def load_data():
    df = pd.read_csv(
        "data/processed/citi_bike_with_weather_2022.csv",
        parse_dates=["started_at", "ended_at", "date"],
    )
    df["date"] = pd.to_datetime(df["date"])
    if "trip_count" not in df.columns:
        df["trip_count"] = 1

    daily = (
        df.groupby("date")
        .agg(trips=("trip_count", "sum"), avg_temp=("avgTemp", "mean"))
        .reset_index()
    )

    return df, daily


df, daily = load_data()


station_counts = (
    df.groupby("start_station_name").agg(count=("trip_count", "sum")).reset_index()
)
top20 = station_counts.nlargest(20, "count").reset_index(drop=True)


# ----- SIDEBAR: PAGE SELECTION -----
page = st.sidebar.selectbox(
    "Choose a page",
    [
        "Intro",
        "Weather & Bike Usage",
        "Most Popular Stations",
        "Interactive Map",
        "Conclusions & Recommendations",
    ],
)

# ---------------- PAGES ----------------
if page == "Intro":
    st.title("Citi Bike 2022 – NYC Dashboard")
    col_text, col_img = st.columns([3, 2], gap="large")

    with col_text:
        st.markdown(
            """
    This interactive dashboard explores CitiBike trips in 2022 and how weather affects ridership.
    Use the sidebar to navigate to the Weather trends, Top stations, Map, and Recommendations.
    """
        )

    with col_img:
        st.image(
            "images/citi_bike_intro.jpg",
            caption="Source: Unsplash – Photo by Lavi Cella",
            width=450,
        )
elif page == "Weather & Bike Usage":
    st.header("Daily Bike Usage Trend (raw + 7-day avg) and Temperature")

    # Diagnostics in sidebar area
    st.sidebar.markdown(
        f"Daily rows: {len(daily)} — date range: {daily['date'].min().date()} to {daily['date'].max().date()}"
    )

    # prepare chart data
    df_plot = daily.sort_values("date")
    df_plot["rides_7d"] = (
        df_plot["trips"].rolling(window=7, min_periods=1, center=False).mean()
    )

    # Plotly: raw line (light), smooth 7d, and temperature on secondary y
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(
        go.Scatter(
            x=df_plot["date"],
            y=df_plot["trips"],
            name="Daily rides (raw)",
            mode="lines",
            line=dict(width=1, color="rgb(31,119,180)"),
            hovertemplate="%{y:,} rides<br>%{x|%Y-%m-%d}<extra></extra>",
        ),
        secondary_y=False,
    )

    fig.add_trace(
        go.Scatter(
            x=df_plot["date"],
            y=df_plot["rides_7d"],
            name="7-day avg (smooth)",
            mode="lines",
            line=dict(width=4, color="rgb(174,199,232)"),
            hovertemplate="%{y:,.0f} (7-day avg)<br>%{x|%Y-%m-%d}<extra></extra>",
        ),
        secondary_y=False,
    )

    if "temperature" in df_plot.columns and not df_plot["temperature"].isna().all():
        fig.add_trace(
            go.Scatter(
                x=df_plot["date"],
                y=df_plot["temperature"],
                name="Avg Temp (°C)",
                mode="lines",
                line=dict(width=2, color="rgb(214,39,40)"),
                hovertemplate="%{y:.1f} °C<br>%{x|%Y-%m-%d}<extra></extra>",
            ),
            secondary_y=True,
        )
        fig.update_yaxes(title_text="Temperature (°C)", secondary_y=True)

    fig.update_yaxes(title_text="Bike rides (count)", secondary_y=False)
    fig.update_layout(
        title="Daily Bike Rides & Temperature",
        height=600,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    st.plotly_chart(fig, width='stretch')

    st.markdown(
        "**Interpretation:** Add 2–3 sentences about trends, peaks and weather relationships."
    )


elif page == "Most Popular Stations":
    st.header("Top 20 Start Stations")
    if "start_station_name" not in df.columns:
        st.warning("Column 'start_station_name' not present in reduced data.")
    else:
        # optional season filter (if season exists)
        if "season" in df.columns:
            seasons = sorted(df["season"].dropna().unique().tolist())
            chosen = st.sidebar.multiselect(
                "Select season(s)", options=seasons, default=seasons
            )
            df_filtered = df[df["season"].isin(chosen)]
        else:
            df_filtered = df

        counts = (
            df_filtered.groupby("start_station_name").size().reset_index(name="count")
        )
        top = counts.nlargest(20, "count").sort_values("count", ascending=True)
        fig_bar = go.Figure(
            go.Bar(
                x=top["count"],
                y=top["start_station_name"],
                orientation="h",
                marker=dict(color=top["count"], colorscale="Blues"),
            )
        )
        fig_bar.update_layout(
            title="Top 20 Start Stations", height=700, margin=dict(l=300)
        )
        st.plotly_chart(fig_bar, width='stretch')
        st.metric("Total rides (current filter)", f"{int(df_filtered.shape[0]):,}")
        st.markdown(
            "**Interpretation:** Add short summary about hotspots and rebalancing candidates."
        )

# ---------------- Interactive map ----------------

elif page == "Interactive Map":
    st.subheader("Citi Bike Trips Map – Kepler.gl")

    custom_css = """
    <style>
        iframe {
            transform: translateZ(0);
        }
    </style>
    """

    try:
        with open(KEPLER_HTML, "r", encoding="utf-8") as f:
            kepler_html = f.read()

        kepler_html = kepler_html.replace(
            "longitude:-122", "longitude:-74.0060"
        ).replace("latitude:37.", "latitude:40.7128")

        st.components.v1.html(custom_css + kepler_html, height=700, scrolling=True)

        st.markdown(
            """
        ### Interpretation  
        New York shows the highest concentration of Citi Bike activity in central Manhattan,
        especially around Midtown and Downtown. High-density areas indicate strong commuter
        and tourist traffic, while outer zones show lower demand.
        """
        )

    except FileNotFoundError:
        st.error(
            "Kepler map file not found. Check that 'Docs/citibike_small_map.html' exists."
        )


# ---------------- Recommendations ----------------
else:
    st.header("Conclusions & Recommendations")
    st.markdown(
        """
    **Key recommendations (examples)**:
    - Prioritize morning rebalancing at major start stations.
    - Increase bike capacity near tourist hubs during warm months.
    - Use short-term weather forecasts to trigger dynamic rebalancing.
    """
    )
