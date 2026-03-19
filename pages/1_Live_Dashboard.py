
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from modules.data_generator import get_der_dataframe
import config
from datetime import datetime


st.set_page_config(page_title="Live Dashboard", layout="wide")

st.markdown('<h1 style="color:#00cc44;">Live Dashboard</h1>',
            unsafe_allow_html=True)
st.markdown("Real-time status of all Distributed Energy Resources")
st.caption(f"Last updated: {datetime.now().strftime('%A %d %B %Y — %H:%M:%S')}")
st.divider()

# Load simulated DER data
df = get_der_dataframe(hours=48)
latest = df.iloc[-1]


# KPI Cards Row
st.subheader("Current Status")
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    solar = latest['solar_kw']
    st.metric(
        label="Solar Output",
        value=f"{solar:.0f} kW",
        delta=f"{solar - df.iloc[-2]['solar_kw']:.0f} kW vs last hour"
    )

with col2:
    wind = latest['wind_kw']
    st.metric(
        label="Wind Output",
        value=f"{wind:.0f} kW",
        delta=f"{wind - df.iloc[-2]['wind_kw']:.0f} kW vs last hour"
    )

with col3:
    bess = latest['bess_kw']
    soc = latest['bess_soc_pct']
    st.metric(
        label="Battery SOC",
        value=f"{soc:.0f}%",
        delta=f"{bess:.0f} kW charging" if bess > 0 else f"{abs(bess):.0f} kW discharging"
    )

with col4:
    load = latest['load_kw']
    st.metric(
        label="Total Load",
        value=f"{load:.0f} kW",
        delta=f"{load - df.iloc[-2]['load_kw']:.0f} kW vs last hour"
    )

with col5:
    grid = latest['grid_kw']
    st.metric(
        label="Grid Import",
        value=f"{grid:.0f} kW",
        delta="Exporting to grid" if grid < 0 else "Importing from grid",
        delta_color="normal" if grid < 0 else "inverse"
    )

st.divider()


# Power Flow Chart
st.subheader("Power Flow — Last 48 Hours")

fig = go.Figure()

fig.add_trace(go.Scatter(
    x=df['timestamp'],
    y=df['solar_kw'],
    name='Solar PV',
    line=dict(color=config.COLOR_SOLAR, width=2),
    fill='tozeroy',
    fillcolor='rgba(244, 197, 66, 0.1)'
))

fig.add_trace(go.Scatter(
    x=df['timestamp'],
    y=df['wind_kw'],
    name='Wind',
    line=dict(color=config.COLOR_WIND, width=2),
    fill='tozeroy',
    fillcolor='rgba(66, 164, 245, 0.1)'
))

fig.add_trace(go.Scatter(
    x=df['timestamp'],
    y=df['load_kw'],
    name='Load Demand',
    line=dict(color=config.COLOR_GRID, width=2, dash='dash'),
))

fig.add_trace(go.Scatter(
    x=df['timestamp'],
    y=df['bess_kw'],
    name='Battery (+ charge / - discharge)',
    line=dict(color=config.COLOR_BESS, width=2),
))

fig.update_layout(
    height=config.CHART_HEIGHT,
    xaxis_title="Time",
    yaxis_title="Power (kW)",
    legend=dict(orientation="h", yanchor="bottom", y=1.02),
    hovermode='x unified',
    plot_bgcolor='white',
    yaxis=dict(gridcolor='#f0f0f0'),
    xaxis=dict(gridcolor='#f0f0f0')
)

st.plotly_chart(fig, use_container_width=True)
st.divider()


# DER Status Cards
st.subheader("DER Device Status")

col1, col2, col3 = st.columns(3)

with col1:
    # Solar PV Card
    solar_pct = (latest['solar_kw'] / config.SOLAR_CAPACITY_KW) * 100
    st.markdown("**Solar PV System**")
    st.progress(int(solar_pct) / 100)
    st.markdown(f"""
    - Output: **{latest['solar_kw']:.0f} kW** of {config.SOLAR_CAPACITY_KW} kW capacity
    - Capacity Factor: **{solar_pct:.1f}%**
    - Today's Generation: **{df.tail(24)['solar_kw'].sum()/60:.0f} kWh**
    - Status: {'🟢 Generating' if latest['solar_kw'] > 0 else '🔴 No Output'}
    """)

    st.divider()

    # Wind Turbine Card
    wind_pct = (latest['wind_kw'] / config.WIND_CAPACITY_KW) * 100
    st.markdown("**Wind Turbine**")
    st.progress(int(min(wind_pct, 100)) / 100)
    st.markdown(f"""
    - Output: **{latest['wind_kw']:.0f} kW** of {config.WIND_CAPACITY_KW} kW capacity
    - Capacity Factor: **{wind_pct:.1f}%**
    - Today's Generation: **{df.tail(24)['wind_kw'].sum()/60:.0f} kWh**
    - Status: {'🟢 Generating' if latest['wind_kw'] > 0 else '🟠 Low Wind'}
    """)

with col2:
    # BESS Card
    soc = latest['bess_soc_pct']
    bess_status = "Charging" if latest['bess_kw'] > 0 else "Discharging" if latest['bess_kw'] < 0 else "Idle"
    bess_color = "normal" if 30 <= soc <= 80 else "inverse"
    st.markdown("**Battery Energy Storage (BESS)**")
    st.progress(int(soc) / 100)
    st.markdown(f"""
    - State of Charge: **{soc:.0f}%**
    - Power: **{abs(latest['bess_kw']):.0f} kW** ({bess_status})
    - Energy Available: **{(soc/100) * config.BESS_CAPACITY_KWH:.0f} kWh**
    - Max Capacity: **{config.BESS_CAPACITY_KWH} kWh**
    - Status: {'🟢 Healthy' if 20 <= soc <= 90 else '🔴 Check Required'}
    """)

    st.divider()

    # EV Fleet Card
    st.markdown("**EV Fleet Charging**")
    st.progress(0.6)
    st.markdown(f"""
    - Charging Load: **{latest['load_kw'] * 0.1:.0f} kW**
    - Vehicles Connected: **3 of 5**
    - Average SOC: **60%**
    - Target SOC by 08:00: **90%**
    - Status: 🟢 Smart Charging Active
    """)

with col3:
    # Grid Connection Card
    grid = latest['grid_kw']
    grid_status = "Exporting" if grid < 0 else "Importing"
    grid_color = "#00cc44" if grid < 0 else "#ff4444"
    st.markdown("**Grid Connection**")
    st.markdown(f"""
    - Power Flow: **{abs(grid):.0f} kW {grid_status}**
    - Connection Limit: **{config.GRID_LIMIT_KW} kW**
    - Utilization: **{(abs(grid)/config.GRID_LIMIT_KW)*100:.1f}%**
    - Frequency: **{config.GRID_FREQUENCY_HZ} Hz**
    - Status: {'🟢 Exporting Clean Energy' if grid < 0 else '🔵 Importing from Grid'}
    """)

    st.divider()

    # Generator Card
    st.markdown("**Backup Generator**")
    st.markdown(f"""
    - Capacity: **{config.GENERATOR_KW} kW**
    - Fuel Level: **85%**
    - Runtime Today: **0 hours**
    - Last Test: **7 days ago**
    - Status: 🟢 Standby — Ready
    """)

st.divider()


# Energy Summary Section
st.subheader("Today's Energy Summary")

col1, col2 = st.columns(2)

with col1:
    # Energy Generation Pie Chart
    solar_today = df.tail(24)['solar_kw'].sum() / 60
    wind_today = df.tail(24)['wind_kw'].sum() / 60
    grid_import = df.tail(24)[df.tail(24)['grid_kw'] > 0]['grid_kw'].sum() / 60

    fig_pie = go.Figure(data=[go.Pie(
        labels=['Solar PV', 'Wind', 'Grid Import'],
        values=[solar_today, wind_today, grid_import],
        hole=0.4,
        marker=dict(colors=[
            config.COLOR_SOLAR,
            config.COLOR_WIND,
            config.COLOR_GRID
        ])
    )])

    fig_pie.update_layout(
        title="Energy Sources Today (kWh)",
        height=350,
        showlegend=True,
        plot_bgcolor='white'
    )

    st.plotly_chart(fig_pie, use_container_width=True)

with col2:
    # Summary Metrics
    total_generation = solar_today + wind_today
    total_load = df.tail(24)['load_kw'].sum() / 60
    self_sufficiency = min(100, (total_generation / total_load) * 100)
    carbon_offset = total_generation * 0.21
    grid_export = df.tail(24)[df.tail(24)['grid_kw'] < 0]['grid_kw'].sum() / 60
    cost_saving = abs(grid_export) * config.ONTARIO_ON_PEAK

    st.markdown("### Key Metrics")
    st.markdown("")

    col_a, col_b = st.columns(2)

    with col_a:
        st.metric(
            label="Total Generation",
            value=f"{total_generation:.0f} kWh"
        )
        st.metric(
            label="Self Sufficiency",
            value=f"{self_sufficiency:.0f}%"
        )
        st.metric(
            label="Carbon Offset",
            value=f"{carbon_offset:.0f} kg CO2"
        )

    with col_b:
        st.metric(
            label="Total Load",
            value=f"{total_load:.0f} kWh"
        )
        st.metric(
            label="Grid Export",
            value=f"{abs(grid_export):.0f} kWh"
        )
        st.metric(
            label="Cost Saving",
            value=f"${cost_saving:.0f} CAD"
        )

    st.divider()
    st.markdown("### Plain English Summary")
    st.success(f"""
    Today your solar panels and wind turbine generated
    **{total_generation:.0f} kWh** of clean electricity.
    Your building consumed **{total_load:.0f} kWh** in total.
    You were **{self_sufficiency:.0f}% self sufficient** —
    meaning you generated {self_sufficiency:.0f}% of your
    own electricity without buying from the grid.
    You avoided **{carbon_offset:.0f} kg of CO2 emissions**
    and saved approximately **${cost_saving:.0f} CAD**
    compared to buying all electricity from the grid.
    """)

st.divider()
st.caption("GreenGrid AI v1.0 — Data refreshes every 30 seconds — All values simulated for demonstration")







