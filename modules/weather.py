
import requests
import pandas as pd
from datetime import datetime, timedelta
import config

OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"

import streamlit as st

@st.cache_data(ttl=3600)
def get_weather_forecast():
    params = {
        "latitude": config.SITE_LATITUDE,
        "longitude": config.SITE_LONGITUDE,
        "hourly": [
            "temperature_2m",
            "cloudcover",
            "windspeed_10m",
            "windspeed_100m",
            "direct_radiation",
            "precipitation_probability"
        ],
        "forecast_days": 3,
        "timezone": "America/Toronto"
    }

    try:
        response = requests.get(OPEN_METEO_URL, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        hourly = data["hourly"]
        df = pd.DataFrame({
            "timestamp": pd.to_datetime(hourly["time"]),
            "temperature_c": hourly["temperature_2m"],
            "cloud_cover_pct": hourly["cloudcover"],
            "wind_speed_10m": hourly["windspeed_10m"],
            "wind_speed_100m": hourly["windspeed_100m"],
            "solar_radiation": hourly["direct_radiation"],
            "precip_probability": hourly["precipitation_probability"]
        })

        return df, True

    except Exception as e:
        print(f"Weather API failed: {e}. Internet may be offline.")
        return get_fallback_weather(), False


def get_fallback_weather():
    now = datetime.now().replace(minute=0, second=0, microsecond=0)
    timestamps = [now + timedelta(hours=i) for i in range(72)]

    df = pd.DataFrame({
        "timestamp": timestamps,
        "temperature_c": [None] * 72,
        "cloud_cover_pct": [None] * 72,
        "wind_speed_10m": [None] * 72,
        "wind_speed_100m": [None] * 72,
        "solar_radiation": [None] * 72,
        "precip_probability": [None] * 72
    })

    return df


def is_weather_offline(is_online):
    return not is_online


def get_weather_summary(df):
    next_24 = df.head(24)
    summary = {
        "avg_temp": round(next_24["temperature_c"].mean(), 1)
        if next_24["temperature_c"].notna().any() else "NOT AVAILABLE",

        "avg_cloud": round(next_24["cloud_cover_pct"].mean(), 1)
        if next_24["cloud_cover_pct"].notna().any() else "NOT AVAILABLE",

        "avg_wind": round(next_24["wind_speed_10m"].mean(), 1)
        if next_24["wind_speed_10m"].notna().any() else "NOT AVAILABLE",

        "max_radiation": round(next_24["solar_radiation"].max(), 0)
        if next_24["solar_radiation"].notna().any() else "NOT AVAILABLE",

        "avg_precip_prob": round(next_24["precip_probability"].mean(), 1)
        if next_24["precip_probability"].notna().any() else "NOT AVAILABLE"
    }
    return summary
