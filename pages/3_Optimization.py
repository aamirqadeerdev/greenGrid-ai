
import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from modules.optimizer import (
    optimize_bess_schedule,
    optimize_ev_charging,
    calculate_peak_shaving,
    get_optimization_explanation,
    get_ontario_prices
)
from modules.forecaster import (
    get_solar_forecast,
    get_wind_forecast,
    get_load_forecast
)
import config

st.set_page_config(page_title="Optimization", layout="wide")

st.markdown('<h1 style="color:#00cc44;">Optimization</h1>',
            unsafe_allow_html=True)
st.markdown("AI-powered schedule for battery charging, EV charging, and peak demand shaving")
st.divider()

with st.spinner("Running forecasting models..."):
    solar_fc = get_solar_forecast(24)
    wind_fc = get_wind_forecast(24)
    load_fc = get_load_forecast(24)

solar_list = solar_fc['forecast'].tolist()
wind_list = wind_fc['forecast'].tolist()
load_list = load_fc['forecast'].tolist()

with st.spinner("Running PuLP optimization engine..."):
    bess_results = optimize_bess_schedule(
        load_list, solar_list, wind_list, hours=24
    )
    ev_results = optimize_ev_charging()
    peak_results = calculate_peak_shaving(
        load_list, bess_results['discharge_kw']
    )
    explanations = get_optimization_explanation(bess_results)

st.subheader("Optimization Results — Today")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="Optimized Energy Cost",
        value=f"CAD {bess_results['total_cost_cad']}",
        delta=f"CAD {bess_results['cost_saving_cad']} saved today",
        delta_color="inverse"
    )

with col2:
    st.metric(
        label="Cost Reduction",
        value=f"{bess_results['saving_pct']}%",
        delta="vs no optimization"
    )

with col3:
    st.metric(
        label="Peak Demand Reduction",
        value=f"{peak_results['peak_reduction_kw']:.0f} kW",
        delta=f"CAD {peak_results['demand_charge_saving_cad']:.0f} saved monthly"
    )

with col4:
    st.metric(
        label="EV Charging Saving",
        value=f"CAD {ev_results['saving_cad']:.2f}",
        delta="smart vs unmanaged charging"
    )

st.divider()

st.subheader("Why the AI Made These Decisions")

for i, explanation in enumerate(explanations):
    st.info(f"Decision {i+1}: {explanation}")

st.divider()

st.subheader("Battery Charging and Discharging Schedule")

hours_labels = [f"{h:02d}:00" for h in range(24)]
prices = get_ontario_prices(24)

fig_bess = go.Figure()

fig_bess.add_trace(go.Bar(
    x=hours_labels,
    y=bess_results['charge_kw'],
    name='Charging (kW)',
    marker_color=config.COLOR_WIND
))

fig_bess.add_trace(go.Bar(
    x=hours_labels,
    y=[-d for d in bess_results['discharge_kw']],
    name='Discharging (kW)',
    marker_color=config.COLOR_BESS
))

fig_bess.add_trace(go.Scatter(
    x=hours_labels,
    y=bess_results['soc_pct'],
    name='Battery SOC (%)',
    line=dict(color=config.COLOR_SOLAR, width=2),
    yaxis='y2'
))

fig_bess.add_trace(go.Scatter(
    x=hours_labels,
    y=[p * 1000 for p in prices],
    name='Price (CAD/MWh)',
    line=dict(color=config.COLOR_GRID, width=1, dash='dot'),
    yaxis='y2'
))

fig_bess.update_layout(
    height=config.CHART_HEIGHT,
    xaxis_title="Hour of Day",
    yaxis=dict(title="Power (kW)", gridcolor='#f0f0f0'),
    yaxis2=dict(
        title="SOC (%) / Price (CAD/MWh)",
        overlaying='y',
        side='right'
    ),
    barmode='relative',
    hovermode='x unified',
    plot_bgcolor='white',
    legend=dict(orientation="h", yanchor="bottom", y=1.02)
)

st.plotly_chart(fig_bess, use_container_width=True)
st.caption("Blue bars = charging during cheap hours. Purple bars = discharging during expensive hours. Yellow line = battery level.")

st.divider()

st.subheader("EV Smart Charging Schedule")

col1, col2 = st.columns(2)

with col1:
    ev_hours = [f"{h:02d}:00" for h in range(12)]

    fig_ev = go.Figure()

    fig_ev.add_trace(go.Bar(
        x=ev_hours,
        y=ev_results['charge_kw'],
        name='EV Charging (kW)',
        marker_color=config.COLOR_EV
    ))

    fig_ev.add_trace(go.Scatter(
        x=ev_hours,
        y=[p * 1000 for p in ev_results['prices']],
        name='Price (CAD/MWh)',
        line=dict(color=config.COLOR_GRID, width=2, dash='dot'),
        yaxis='y2'
    ))

    fig_ev.update_layout(
        height=350,
        xaxis_title="Hour",
        yaxis=dict(title="Charging Power (kW)", gridcolor='#f0f0f0'),
        yaxis2=dict(
            title="Price (CAD/MWh)",
            overlaying='y',
            side='right'
        ),
        hovermode='x unified',
        plot_bgcolor='white',
        legend=dict(orientation="h", yanchor="bottom", y=1.02)
    )

    st.plotly_chart(fig_ev, use_container_width=True)

with col2:
    st.markdown("### EV Charging Summary")
    st.markdown("")

    st.metric(
        label="Energy Needed",
        value=f"{ev_results['energy_needed_kwh']} kWh"
    )
    st.metric(
        label="Smart Charging Cost",
        value=f"CAD {ev_results['optimized_cost_cad']}"
    )
    st.metric(
        label="Unmanaged Cost",
        value=f"CAD {ev_results['unmanaged_cost_cad']}"
    )
    st.metric(
        label="Money Saved",
        value=f"CAD {ev_results['saving_cad']}"
    )

    st.success(f"""
    Smart Charging Plan:
    Vehicle will be charged to
    {ev_results['target_soc_pct']}% by
    {ev_results['departure_hour']:02d}:00
    departure time using the cheapest
    available electricity hours.
    """)

st.divider()

st.subheader("Peak Demand Shaving")

fig_peak = go.Figure()

fig_peak.add_trace(go.Scatter(
    x=hours_labels,
    y=load_list[:24],
    name='Original Load',
    line=dict(color=config.COLOR_GRID, width=2, dash='dash')
))

fig_peak.add_trace(go.Scatter(
    x=hours_labels,
    y=peak_results['shaved_load'][:24],
    name='Load After Peak Shaving',
    line=dict(color=config.COLOR_NORMAL, width=2),
    fill='tozeroy',
    fillcolor='rgba(0, 204, 68, 0.1)'
))

fig_peak.add_hline(
    y=peak_results['shaved_peak_kw'],
    line_dash="dot",
    line_color=config.COLOR_NORMAL,
    annotation_text=f"New Peak: {peak_results['shaved_peak_kw']:.0f} kW"
)

fig_peak.add_hline(
    y=peak_results['original_peak_kw'],
    line_dash="dot",
    line_color=config.COLOR_CRITICAL,
    annotation_text=f"Original Peak: {peak_results['original_peak_kw']:.0f} kW"
)

fig_peak.update_layout(
    height=config.CHART_HEIGHT,
    xaxis_title="Hour of Day",
    yaxis_title="Power (kW)",
    hovermode='x unified',
    plot_bgcolor='white',
    yaxis=dict(gridcolor='#f0f0f0'),
    xaxis=dict(gridcolor='#f0f0f0'),
    legend=dict(orientation="h", yanchor="bottom", y=1.02)
)

st.plotly_chart(fig_peak, use_container_width=True)

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        label="Original Peak Demand",
        value=f"{peak_results['original_peak_kw']} kW"
    )

with col2:
    st.metric(
        label="Peak After Shaving",
        value=f"{peak_results['shaved_peak_kw']} kW"
    )

with col3:
    st.metric(
        label="Monthly Demand Charge Saving",
        value=f"CAD {peak_results['demand_charge_saving_cad']:.0f}"
    )

st.divider()

st.subheader("Ontario Electricity Prices — Today")

price_colors = []
for p in prices:
    if p == config.ONTARIO_OFF_PEAK:
        price_colors.append(config.COLOR_NORMAL)
    elif p == config.ONTARIO_MID_PEAK:
        price_colors.append(config.COLOR_WARNING)
    else:
        price_colors.append(config.COLOR_CRITICAL)

fig_price = go.Figure()

fig_price.add_trace(go.Bar(
    x=hours_labels,
    y=[p * 100 for p in prices],
    name='Price (cents/kWh)',
    marker_color=price_colors
))

fig_price.update_layout(
    height=300,
    xaxis_title="Hour of Day",
    yaxis_title="Price (cents/kWh)",
    plot_bgcolor='white',
    yaxis=dict(gridcolor='#f0f0f0'),
    xaxis=dict(gridcolor='#f0f0f0')
)

st.plotly_chart(fig_price, use_container_width=True)
st.caption("Green = Off-Peak (cheap). Orange = Mid-Peak. Red = On-Peak (expensive). Battery charges green and discharges red.")

st.divider()

st.subheader("Complete Optimization Summary")

st.success(f"""
Today's Optimization Plan in Plain English:

Your battery will charge during the cheap overnight hours
when electricity costs only CAD {config.ONTARIO_OFF_PEAK}/kWh.
It will discharge during the expensive evening peak hours
when electricity costs CAD {config.ONTARIO_ON_PEAK}/kWh
saving you CAD {bess_results['cost_saving_cad']} today
which is a {bess_results['saving_pct']}% reduction
in your electricity bill.

Your electric vehicles will be smart charged overnight
during the cheapest hours saving an additional
CAD {ev_results['saving_cad']:.2f} compared to
unmanaged charging.

Peak demand shaving will reduce your maximum demand
from {peak_results['original_peak_kw']:.0f} kW to
{peak_results['shaved_peak_kw']:.0f} kW saving
approximately CAD {peak_results['demand_charge_saving_cad']:.0f}
in monthly demand charges.
""")

st.caption("GreenGrid AI v1.0 — Optimization powered by PuLP Linear Programming")
