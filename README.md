# NYC CitiBike 2022 — Full Data Pipeline, Visualization, and Dashboard
Project


# Citi Bike NYC 2022 Dashboard

This project analyzes Citi Bike trip data for 2022 and produces a series
of insights and visualizations using Python.

## 📁 Project Structure

## 🚴 Data Source

The dataset is collected from the NYC Citi Bike system. All files end
with `.csv`.

## 🔧 Technologies Used

- Python 3.x  
- Pandas  
- Matplotlib / Plotly  
- Streamlit (for app)  
- Git & GitHub

## ▶ Running the Streamlit App

\`\`\`bash streamlit run dashboard/app.py

# 🚴 NYC CitiBike Trips 2022 — Complete Analytics & Dashboard Project

**CareerFoundry Data Analytics Program – Achievement 2 (Completed up to
Chapter 6)**  
**Author:** Biswajit Das

This repository contains the complete workflow for analyzing New York
City’s CitiBike usage in 2022, combining trip data with weather
patterns, building geospatial visualizations, and deploying an
interactive dashboard using Streamlit.

The work in this project demonstrates practical skills in:

- Data engineering  
- API usage  
- Version control  
- Environment management  
- Data visualization (Plotly, Kepler.gl)  
- Dashboard development (Streamlit)  
- Project structuring & reproducibility

This project is part of my ongoing portfolio and will be extended in
**Chapter 7** to include multi-page dashboards, deployment, and
presentation delivery.

------------------------------------------------------------------------

# 🎯 Project Objectives

1.  **Collect, clean, and merge** CitiBike trip data for all months in
    2022.  
2.  Retrieve **daily average temperature** data and combine it with bike
    usage.  
3.  Build **interactive visualizations** using Plotly and Kepler.gl.  
4.  Create a **Streamlit dashboard** with charts + an embedded
    geospatial map.  
5.  Organize the repository according to best practices.  
6.  Work in a reproducible Conda environment and track progress with
    Git/GitHub.

------------------------------------------------------------------------

# 📚 What I Learned (Summary of Skills Used)

## **🛠️ Data Engineering & Analysis**

- Working with large CSV files (\>25M rows)  
- Reading, batching, and merging multiple datasets  
- Converting timestamps, extracting dates, building aggregations  
- Clean column types for analysis and modeling  
- Joining external weather data into the trip dataset  
- Creating daily aggregated datasets for visualizations

## **📊 Data Visualization**

- Building **horizontal bar charts** for top stations (Plotly)  
- Creating **dual-axis time-series charts** (bike usage + temperature)  
- Understanding layouts, titles, axis formatting, and interactivity  
- Creating and configuring **Kepler.gl maps**  
- Saving Kepler configs & HTML outputs

## **🌐 Dashboard Development**

- Creating `citi_dashboard.py` application  
- Structuring Streamlit apps  
- Embedding Plotly charts  
- Embedding Kepler.gl HTML maps  
- Managing file paths and assets

## **🧰 Tools & Technologies**

- Python  
- pandas  
- numpy  
- plotly  
- keplergl  
- streamlit  
- pathlib  
- JupyterLab  
- Conda environment  
- Git & GitHub  
- Quarto for documentation

------------------------------------------------------------------------

# 🧪 Detailed Workflow (Everything Completed in This Project)

## **1. Environment Setup**

- Created and activated a dedicated Conda environment  
- Installed required libraries (`pandas`, `plotly`, `streamlit`,
  `keplergl`)  
- Launched JupyterLab for analysis

------------------------------------------------------------------------

## **2. Data Collection**

- Downloaded all CitiBike 2022 monthly trip data  
- Removed large files (\>25 MB) before Git push (to meet GitHub
  limits)  
- Path: `data/raw/`

------------------------------------------------------------------------

## **3. Data Cleaning & Integration**

Steps performed in notebook:

- Loaded monthly CSVs  
- Standardized column names  
- Handled missing values  
- Converted timestamps  
- Extracted date column  
- Grouped and aggregated per-day bike usage  
- Loaded merged weather data  
- Joined bike + weather datasets  
- Exported `citibike_with_weather_merged.csv`

> *Stored under:* `data/processed/`

------------------------------------------------------------------------

## **4. Geospatial Visualization — Kepler.gl**

- Loaded trip data  
- Applied filtering and styling  
- Created interactive map  
- Generated a **Kepler config object**  
- Exported **map HTML + config JSON**  
- Saved under `docs/`

------------------------------------------------------------------------

## **5. Visualizations in Jupyter**

### **Top 20 Start Stations (Plotly bar chart)**

- Grouped station frequency  
- Created horizontal bar chart  
- Exported `top20.csv` → stored in `/docs`

### **Dual-Axis Line Chart (Plotly)**

- Daily bike rides vs. temperature  
- Used `make_subplots()` with secondary y-axis  
- Exported for Streamlit use

------------------------------------------------------------------------

## **6. Streamlit Dashboard Development**

File: `citi_dashboard.py`

Dashboard includes:

- Page config  
- Titles + description  
- Loaded merged data  
- Imported top stations CSV  
- Displayed bar chart  
- Displayed dual-axis time series  
- Embedded Kepler map HTML

Running the dashboard: Link:
