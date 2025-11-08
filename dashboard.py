import streamlit as st
import pandas as pd
import requests
import plotly.express as px

# ---------------------------
# 🌍 STREAMLIT PAGE CONFIG
# ---------------------------
st.set_page_config(page_title="🌍 Advanced AQI Dashboard", layout="wide")

st.title("🌍 Advanced Air Quality Index (AQI) Dashboard")
st.markdown("Monitor real-time **air quality** and **weather** conditions across major cities including Delhi & Gurgaon.")

# ---------------------------
# 🔑 API KEYS (replace with your own)
# ---------------------------
waqi_token = "373f3d81e7f749f3e9c49bc3f1a3fee5950a1299"
weather_api_key = "38432c8e09ad54d478eaab031fc2726d"  # 👉 get from https://openweathermap.org/api

# ---------------------------
# 📍 SIDEBAR CONTROLS
# ---------------------------
st.sidebar.header("Settings")
cities = st.sidebar.multiselect(
    "Select locations to compare AQI:",
    ["Delhi", "Gurgaon", "Mumbai", "Chennai", "Bangalore", "Kolkata", "London", "New York", "Beijing"],
    default=["Delhi", "Gurgaon", "Mumbai"]
)

# ---------------------------
# 🌫️ FETCH AQI + POLLUTANTS
# ---------------------------
@st.cache_data
def get_city_aqi(city):
    url = f"https://api.waqi.info/feed/{city}/?token={waqi_token}"
    response = requests.get(url)
    data = response.json()
    if data["status"] != "ok":
        return None
    
    city_data = data["data"]
    pollutants = city_data.get("iaqi", {})
    result = {
        "City": city_data["city"]["name"],
        "AQI": city_data["aqi"],
        "PM2.5": pollutants.get("pm25", {}).get("v"),
        "PM10": pollutants.get("pm10", {}).get("v"),
        "CO": pollutants.get("co", {}).get("v"),
        "NO2": pollutants.get("no2", {}).get("v"),
        "SO2": pollutants.get("so2", {}).get("v"),
        "O3": pollutants.get("o3", {}).get("v"),
        "Lat": city_data["city"]["geo"][0],
        "Lon": city_data["city"]["geo"][1]
    }
    return result

# ---------------------------
# ☁️ FETCH WEATHER DATA
# ---------------------------
@st.cache_data
def get_weather_data(lat, lon):
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={weather_api_key}&units=metric"
    response = requests.get(url)
    if response.status_code == 200:
        w = response.json()
        return {
            "Temp (°C)": w["main"]["temp"],
            "Humidity (%)": w["main"]["humidity"],
            "Wind Speed (m/s)": w["wind"]["speed"]
        }
    else:
        return {}

# ---------------------------
# 📊 COMBINE & DISPLAY DATA
# ---------------------------
aqi_data = []
for city in cities:
    aqi_info = get_city_aqi(city)
    if aqi_info:
        weather = get_weather_data(aqi_info["Lat"], aqi_info["Lon"])
        aqi_info.update(weather)
        aqi_data.append(aqi_info)

if len(aqi_data) == 0:
    st.error("No data available. Please check your API tokens or city names.")
else:
    df = pd.DataFrame(aqi_data)

    # --- AQI Condition ---
    def aqi_status(aqi):
        if aqi <= 50:
            return "🟢 Good"
        elif aqi <= 100:
            return "🟡 Moderate"
        elif aqi <= 150:
            return "🟠 Unhealthy (Sensitive)"
        elif aqi <= 200:
            return "🔴 Unhealthy"
        elif aqi <= 300:
            return "🟣 Very Unhealthy"
        else:
            return "⚫ Hazardous"

    df["Status"] = df["AQI"].apply(aqi_status)

    # --- Display Overview Table ---
    st.subheader("📋 AQI and Weather Summary")
    st.dataframe(df)

    # --- Display Metrics for Each City ---
    st.subheader("🏙️ City-wise AQI Overview")
    cols = st.columns(len(df))
    for idx, row in df.iterrows():
        with cols[idx]:
            st.metric(row["City"], f"{row['AQI']} ({row['Status']})", help="Air Quality Index")

    # --- AQI Comparison Chart ---
    st.subheader("📈 AQI Comparison")
    fig = px.bar(df, x="City", y="AQI", color="Status", text="AQI", title="City-wise AQI Levels")
    fig.update_traces(textposition="outside")
    st.plotly_chart(fig, use_container_width=True)

    # --- Pollutant Breakdown ---
    st.subheader("💨 Pollutant Breakdown (µg/m³)")
    pollutant_cols = ["PM2.5", "PM10", "CO", "NO2", "SO2", "O3"]
    df_pollutants = df.melt(id_vars=["City"], value_vars=pollutant_cols, var_name="Pollutant", value_name="Value")
    fig_poll = px.bar(df_pollutants, x="City", y="Value", color="Pollutant", barmode="group", title="Major Pollutants by City")
    st.plotly_chart(fig_poll, use_container_width=True)

    # --- Weather Summary Chart ---
    st.subheader("☁️ Weather Conditions")
    weather_cols = ["Temp (°C)", "Humidity (%)", "Wind Speed (m/s)"]
    df_weather = df.melt(id_vars=["City"], value_vars=weather_cols, var_name="Weather Metric", value_name="Value")
    fig_weather = px.bar(df_weather, x="City", y="Value", color="Weather Metric", barmode="group", title="Weather Conditions by City")
    st.plotly_chart(fig_weather, use_container_width=True)

st.markdown("---")
st.caption("Data source: [World Air Quality Index Project](https://aqicn.org/) & [OpenWeatherMap](https://openweathermap.org/)")
import pandas as pd

st.subheader("📈 Historical AQI + Weather Trends")

try:
    df_hist = pd.read_csv("aqi_weather_log.csv", parse_dates=["timestamp"])
    df_hist["timestamp"] = pd.to_datetime(df_hist["timestamp"])

    # Line chart of AQI over time
    fig_hist = px.line(
        df_hist,
        x="timestamp",
        y="aqi",
        color="city",
        title="AQI Trends Over Time",
        markers=True
    )
    st.plotly_chart(fig_hist, use_container_width=True)

    # Temperature & Humidity trends
    weather_cols = [col for col in ["temp", "humidity"] if col in df_hist.columns]
    if weather_cols:
        df_weather = df_hist.melt(id_vars=["timestamp", "city"],
                                  value_vars=weather_cols,
                                  var_name="Metric", value_name="Value")
        fig_weather = px.line(df_weather, x="timestamp", y="Value", color="city", line_dash="Metric",
                              title="Temperature and Humidity Trends Over Time")
        st.plotly_chart(fig_weather, use_container_width=True)
    else:
        st.warning("No weather data found yet. Wait for logger to collect data.")

except FileNotFoundError:
    st.warning("⚠️ No historical data found yet. Run `aqi_data_logger.py` first.")
