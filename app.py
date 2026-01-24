# ----- IMPORTS -----
import streamlit as st
import pandas as pd
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import streamlit.components.v1 as components

# ----- PAGE CONFIG -----
st.set_page_config(
    page_title="Citi Bike 2022 – NYC Dashboard",
    layout="wide"
)

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
        .agg(
            trips=("trip_count", "sum"),
            avg_temp=("avgTemp", "mean"),
        )
        .reset_index()
    )

    return df.copy(), daily.copy()


df, daily = load_data()

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
            This interactive dashboard explores Citi Bike trips in 2022 and
            how weather affects ridership.

            Use the sidebar to navigate between trends, stations, maps,
            and recommendations.
            """
        )

    with col_img:
        st.image(
            "images/citi_bike_intro.jpg",
            caption="Source: Unsplash – Photo by Lavi Cella",
            width=450,
        )

# ---------------- Weather & Bike Usage ----------------
elif page == "Weather & Bike Usage":
    st.header("Daily Bike Usage Trend and Temperature")

    st.sidebar.markdown(
        f"Daily rows: {len(daily)}  \n"
        f"Date range: {daily['date'].min().date()} → {daily['date'].max().date()}"
    )

    df_plot = daily.sort_values("date").copy()
    df_plot["rides_7d"] = (
        df_plot["trips"]
        .rolling(window=7, min_periods=1)
        .mean()
    )

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
            name="7-day avg",
            mode="lines",
            line=dict(width=4, color="rgb(174,199,232)"),
            hovertemplate="%{y:,.0f}<br>%{x|%Y-%m-%d}<extra></extra>",
        ),
        secondary_y=False,
    )

    if not df_plot["avg_temp"].isna().all():
        fig.add_trace(
            go.Scatter(
                x=df_plot["date"],
                y=df_plot["avg_temp"],
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
        title="Daily Bike Rides and Temperature",
        height=600,
        template="plotly_white",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
        ),
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
        theme=None,
        key="weather_plot",
    )

    st.markdown(
        "**Interpretation:** Describe seasonality, peaks, and the relationship with temperature."
    )

# ---------------- Most Popular Stations ----------------
elif page == "Most Popular Stations":
    st.header("Top 20 Start Stations")

    if "start_station_name" not in df.columns:
        st.warning("Column 'start_station_name' not found.")
    else:
        df_work = df.copy()

        if "season" in df_work.columns:
            seasons = sorted(df_work["season"].dropna().unique())
            chosen = st.sidebar.multiselect(
                "Select season(s)",
                options=seasons,
                default=seasons,
            )
            df_work = df_work[df_work["season"].isin(chosen)]

        counts = (
            df_work
            .groupby("start_station_name")
            .size()
            .reset_index(name="count")
        )

        top = (
            counts
            .nlargest(20, "count")
            .sort_values("count", ascending=True)
        )

        fig_bar = go.Figure(
            go.Bar(
                x=top["count"],
                y=top["start_station_name"],
                orientation="h",
                marker=dict(
                    color=top["count"],
                    colorscale="Blues",
                ),
            )
        )

        fig_bar.update_layout(
            title="Top 20 Start Stations",
            height=700,
            margin=dict(l=300),
            template="plotly_white",
        )

        st.plotly_chart(
            fig_bar,
            use_container_width=True,
            theme=None,
            key="stations_plot",
        )

        st.metric(
            "Total rides (current filter)",
            f"{int(df_work.shape[0]):,}",
        )

        st.markdown(
            "**Interpretation:** Identify demand hotspots and rebalancing priorities."
        )

# ---------------- Interactive Map ----------------
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

        kepler_html = (
            kepler_html
            .replace("longitude:-122", "longitude:-74.0060")
            .replace("latitude:37.", "latitude:40.7128")
        )

        components.html(
            custom_css + kepler_html,
            height=700,
            scrolling=True,
        )

        st.markdown(
            """
            **Interpretation:**  
            Activity concentrates in Manhattan, reflecting commuting
            and tourism demand. Peripheral zones show lower density.
            """
        )

    except FileNotFoundError:
        st.error("Kepler map file not found.")

# ---------------- Conclusions ----------------
else:
    st.header("Conclusions & Recommendations")

    st.markdown(
        """
        **Key recommendations**:

        - Prioritize morning rebalancing at high-demand stations  
        - Increase capacity near tourist hubs during warm months  
        - Use short-term weather forecasts for dynamic operations  
        """
    )
