

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from modules.weather import get_weather_forecast, is_weather_offline, get_weather_summary
from modules.forecaster import (
    get_solar_forecast,
    get_wind_forecast,
    get_load_forecast,
    get_net_load_forecast,
    get_forecast_summary
)
import config

# ─── Page Configuration ──────────────────────────────────────
st.set_page_config(page_title="Forecasting", layout="wide")

st.markdown('<h1 style="color:#00cc44;">Forecasting</h1>',
            unsafe_allow_html=True)
st.markdown("24 and 48 hour predictions for solar, wind, and load demand")
st.divider()

# ─── Fetch Weather Data ───────────────────────────────────────
with st.spinner("Fetching live weather data from Open-Meteo..."):
    weather_df, is_online = get_weather_forecast()

# ─── Check Internet Connection ───────────────────────────────
if is_weather_offline(is_online):
    st.error("""
    Weather data is currently unavailable.
    Please check your internet connection.
    The forecast will update automatically
    when the connection is restored.
    """)
    st.stop()

st.success("Live weather data loaded successfully from Open-Meteo API")

# ─── Forecast Horizon Selector ───────────────────────────────
horizon = st.radio(
    "Select Forecast Horizon",
    options=[24, 48],
    format_func=lambda x: f"{x} Hours",
    horizontal=True
)

st.divider()

# ─── Generate Forecasts ───────────────────────────────────────
with st.spinner("Running Prophet ML forecasting models..."):
    solar_fc = get_solar_forecast(horizon)
    wind_fc = get_wind_forecast(horizon)
    load_fc = get_load_forecast(horizon)
    net_load_fc = get_net_load_forecast(horizon)
    summary = get_forecast_summary(solar_fc, wind_fc, load_fc)
    weather_summary = get_weather_summary(weather_df)

# ─── Weather Summary Row ─────────────────────────────────────
st.subheader("Current Weather Conditions — Ontario, Canada")

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric(
        label="Average Temperature",
        value=f"{weather_summary['avg_temp']} °C"
        if weather_summary['avg_temp'] != "NOT AVAILABLE"
        else "NOT AVAILABLE"
    )

with col2:
    st.metric(
        label="Cloud Cover",
        value=f"{weather_summary['avg_cloud']} %"
        if weather_summary['avg_cloud'] != "NOT AVAILABLE"
        else "NOT AVAILABLE"
    )

with col3:
    st.metric(
        label="Wind Speed",
        value=f"{weather_summary['avg_wind']} m/s"
        if weather_summary['avg_wind'] != "NOT AVAILABLE"
        else "NOT AVAILABLE"
    )

with col4:
    st.metric(
        label="Max Solar Radiation",
        value=f"{weather_summary['max_radiation']} W/m²"
        if weather_summary['max_radiation'] != "NOT AVAILABLE"
        else "NOT AVAILABLE"
    )

with col5:
    st.metric(
        label="Rain Probability",
        value=f"{weather_summary['avg_precip_prob']} %"
        if weather_summary['avg_precip_prob'] != "NOT AVAILABLE"
        else "NOT AVAILABLE"
    )

st.divider()

# ─── Forecast KPI Cards ───────────────────────────────────────
st.subheader(f"Forecast Summary — Next {horizon} Hours")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="Expected Solar Generation",
        value=f"{summary['total_solar_kwh']:.0f} kWh"
    )

with col2:
    st.metric(
        label="Expected Wind Generation",
        value=f"{summary['total_wind_kwh']:.0f} kWh"
    )

with col3:
    st.metric(
        label="Peak Load Expected",
        value=f"{summary['peak_load_kw']:.0f} kW",
        delta=f"at {summary['peak_load_hour']}"
    )

with col4:
    st.metric(
        label="Total Renewable Generation",
        value=f"{summary['total_renewable_kwh']:.0f} kWh"
    )

st.divider()

# ─── Solar Forecast Chart ─────────────────────────────────────
st.subheader("Solar PV Generation Forecast")

fig_solar = go.Figure()

fig_solar.add_trace(go.Scatter(
    x=solar_fc['timestamp'],
    y=solar_fc['upper_bound'],
    name='Upper Bound',
    line=dict(color='rgba(244,197,66,0.3)', width=0),
    showlegend=False
))

fig_solar.add_trace(go.Scatter(
    x=solar_fc['timestamp'],
    y=solar_fc['lower_bound'],
    name='Confidence Interval',
    fill='tonexty',
    fillcolor='rgba(244,197,66,0.2)',
    line=dict(color='rgba(244,197,66,0.3)', width=0)
))

fig_solar.add_trace(go.Scatter(
    x=solar_fc['timestamp'],
    y=solar_fc['forecast'],
    name='Solar Forecast',
    line=dict(color=config.COLOR_SOLAR, width=2)
))

fig_solar.update_layout(
    height=config.CHART_HEIGHT,
    xaxis_title="Time",
    yaxis_title="Power (kW)",
    hovermode='x unified',
    plot_bgcolor='white',
    yaxis=dict(gridcolor='#f0f0f0'),
    xaxis=dict(gridcolor='#f0f0f0'),
    legend=dict(orientation="h", yanchor="bottom", y=1.02)
)

st.plotly_chart(fig_solar, use_container_width=True)
st.caption("Shaded area shows 80% confidence interval — actual output will likely fall within this range")

st.divider()

# ─── Wind Forecast Chart ──────────────────────────────────────
st.subheader("Wind Turbine Generation Forecast")

fig_wind = go.Figure()

fig_wind.add_trace(go.Scatter(
    x=wind_fc['timestamp'],
    y=wind_fc['upper_bound'],
    name='Upper Bound',
    line=dict(color='rgba(66,164,245,0.3)', width=0),
    showlegend=False
))

fig_wind.add_trace(go.Scatter(
    x=wind_fc['timestamp'],
    y=wind_fc['lower_bound'],
    name='Confidence Interval',
    fill='tonexty',
    fillcolor='rgba(66,164,245,0.2)',
    line=dict(color='rgba(66,164,245,0.3)', width=0)
))

fig_wind.add_trace(go.Scatter(
    x=wind_fc['timestamp'],
    y=wind_fc['forecast'],
    name='Wind Forecast',
    line=dict(color=config.COLOR_WIND, width=2)
))

fig_wind.update_layout(
    height=config.CHART_HEIGHT,
    xaxis_title="Time",
    yaxis_title="Power (kW)",
    hovermode='x unified',
    plot_bgcolor='white',
    yaxis=dict(gridcolor='#f0f0f0'),
    xaxis=dict(gridcolor='#f0f0f0'),
    legend=dict(orientation="h", yanchor="bottom", y=1.02)
)

st.plotly_chart(fig_wind, use_container_width=True)
st.caption("Wind forecast has wider confidence interval than solar due to natural wind variability")

st.divider()

# ─── Load Forecast Chart ──────────────────────────────────────
st.subheader("Load Demand Forecast")

fig_load = go.Figure()

fig_load.add_trace(go.Scatter(
    x=load_fc['timestamp'],
    y=load_fc['upper_bound'],
    name='Upper Bound',
    line=dict(color='rgba(245,66,66,0.3)', width=0),
    showlegend=False
))

fig_load.add_trace(go.Scatter(
    x=load_fc['timestamp'],
    y=load_fc['lower_bound'],
    name='Confidence Interval',
    fill='tonexty',
    fillcolor='rgba(245,66,66,0.2)',
    line=dict(color='rgba(245,66,66,0.3)', width=0)
))

fig_load.add_trace(go.Scatter(
    x=load_fc['timestamp'],
    y=load_fc['forecast'],
    name='Load Forecast',
    line=dict(color=config.COLOR_GRID, width=2)
))

fig_load.update_layout(
    height=config.CHART_HEIGHT,
    xaxis_title="Time",
    yaxis_title="Power (kW)",
    hovermode='x unified',
    plot_bgcolor='white',
    yaxis=dict(gridcolor='#f0f0f0'),
    xaxis=dict(gridcolor='#f0f0f0'),
    legend=dict(orientation="h", yanchor="bottom", y=1.02)
)

st.plotly_chart(fig_load, use_container_width=True)
st.caption("Load forecast shows expected electricity consumption — peaks at morning and evening hours")

st.divider()

# ─── Net Load Forecast Chart ──────────────────────────────────
st.subheader("Net Load Forecast — Grid Import Required")

fig_net = go.Figure()

fig_net.add_trace(go.Scatter(
    x=net_load_fc['timestamp'],
    y=net_load_fc['forecast'],
    name='Net Load',
    line=dict(color=config.COLOR_BESS, width=2),
    fill='tozeroy',
    fillcolor='rgba(123,66,245,0.1)'
))

fig_net.update_layout(
    height=config.CHART_HEIGHT,
    xaxis_title="Time",
    yaxis_title="Power (kW)",
    hovermode='x unified',
    plot_bgcolor='white',
    yaxis=dict(gridcolor='#f0f0f0'),
    xaxis=dict(gridcolor='#f0f0f0')
)

st.plotly_chart(fig_net, use_container_width=True)
st.caption("Net load shows how much electricity must be imported from the grid after using all renewable generation")

st.divider()

# ─── Weather Details Chart ────────────────────────────────────
st.subheader("Weather Forecast — Next 72 Hours")

fig_weather = go.Figure()

fig_weather.add_trace(go.Scatter(
    x=weather_df['timestamp'],
    y=weather_df['solar_radiation'],
    name='Solar Radiation (W/m²)',
    line=dict(color=config.COLOR_SOLAR, width=2),
    yaxis='y'
))

fig_weather.add_trace(go.Scatter(
    x=weather_df['timestamp'],
    y=weather_df['wind_speed_100m'],
    name='Wind Speed 100m (m/s)',
    line=dict(color=config.COLOR_WIND, width=2),
    yaxis='y2'
))

fig_weather.add_trace(go.Scatter(
    x=weather_df['timestamp'],
    y=weather_df['temperature_c'],
    name='Temperature (°C)',
    line=dict(color=config.COLOR_GRID, width=2, dash='dot'),
    yaxis='y2'
))

fig_weather.update_layout(
    height=config.CHART_HEIGHT,
    xaxis_title="Time",
    yaxis=dict(
        title="Solar Radiation (W/m²)",
        gridcolor='#f0f0f0'
    ),
    yaxis2=dict(
        title="Wind Speed (m/s) / Temperature (°C)",
        overlaying='y',
        side='right'
    ),
    hovermode='x unified',
    plot_bgcolor='white',
    legend=dict(orientation="h", yanchor="bottom", y=1.02)
)

st.plotly_chart(fig_weather, use_container_width=True)
st.caption("Real weather data from Open-Meteo API — updates every hour automatically")

st.divider()

# ─── Plain English Summary ────────────────────────────────────
st.subheader("Forecast Summary in Plain English")

renewable_pct = (summary['total_renewable_kwh'] /
                (summary['total_renewable_kwh'] +
                 summary['peak_load_kw'])) * 100

st.info(f"""
In the next {horizon} hours your solar panels are expected
to generate **{summary['total_solar_kwh']:.0f} kWh** and your
wind turbine is expected to generate **{summary['total_wind_kwh']:.0f} kWh**
of clean electricity.

Your building will reach its peak demand of
**{summary['peak_load_kw']:.0f} kW** at **{summary['peak_load_hour']}**
so make sure your battery is charged before that time.

Total renewable generation of **{summary['total_renewable_kwh']:.0f} kWh**
will help reduce your grid electricity purchases significantly
over the next {horizon} hours.

Current weather conditions show an average temperature of
**{weather_summary['avg_temp']} °C** with **{weather_summary['avg_cloud']}%**
cloud cover and wind speeds of **{weather_summary['avg_wind']} m/s.**
""")

st.caption("GreenGrid AI v1.0 — Forecasts powered by Prophet ML + Open-Meteo Weather API")
