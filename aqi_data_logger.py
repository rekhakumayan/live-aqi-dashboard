import requests
import pandas as pd
import time
from datetime import datetime

# --- API KEYS ---
AQI_TOKEN = "373f3d81e7f749f3e9c49bc3f1a3fee5950a1299"  # your AQI token
WEATHER_KEY = "38432c8e09ad54d478eaab031fc2726d"           # 👈 get from https://openweathermap.org/api

# --- Cities to Track ---
cities = ["Delhi", "Gurgaon", "Mumbai"]

# --- Function to Fetch AQI ---
def get_aqi(city):
    url = f"https://api.waqi.info/feed/{city}/?token={AQI_TOKEN}"
    response = requests.get(url)
    data = response.json()

    if data["status"] != "ok":
        print(f"⚠️ AQI not available for {city}")
        return None

    aqi = data["data"]["aqi"]
    lat, lon = data["data"]["city"]["geo"]

    # --- Fetch Weather Data ---
    wurl = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={WEATHER_KEY}&units=metric"
    wresponse = requests.get(wurl)
    wdata = wresponse.json()

    if wdata.get("cod") != 200:
        print(f"⚠️ Weather not available for {city}")
        temp = humidity = wind = None
    else:
        temp = wdata.get("main", {}).get("temp")
        humidity = wdata.get("main", {}).get("humidity")
        wind = wdata.get("wind", {}).get("speed")

    info = {
        "timestamp": datetime.now(),
        "city": city,
        "aqi": aqi,
        "temp": temp,
        "humidity": humidity,
        "wind_speed": wind
    }

    return info


# --- Function to Log Data ---
def log_data():
    filename = "aqi_weather_log.csv"

    while True:
        all_data = []
        for city in cities:
            info = get_aqi(city)
            if info:
                all_data.append(info)
                print(f"✅ Logged {city}: AQI={info['aqi']}, Temp={info['temp']}°C")

        if all_data:
            df = pd.DataFrame(all_data)
            df.to_csv(filename, mode="a", header=not pd.io.common.file_exists(filename), index=False)
            print(f"✅ Data saved to {filename} ({len(all_data)} records)\n")

        # Wait 10 minutes before next run
        time.sleep(600)  # 600 seconds = 10 minutes


if __name__ == "__main__":
    log_data()
