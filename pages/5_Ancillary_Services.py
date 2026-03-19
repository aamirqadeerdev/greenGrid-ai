

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from modules.ancillary import (
    get_grid_frequency,
    get_voltage_status,
    get_spinning_reserve,
    get_ancillary_services_status,
    generate_grid_events,
    get_frequency_history,
    get_ancillary_revenue
)
import config

# ─── Page Configuration ──────────────────────────────────────
st.set_page_config(page_title="Ancillary Services", layout="wide")

st.markdown('<h1 style="color:#00cc44;">Ancillary Services</h1>',
            unsafe_allow_html=True)
st.markdown("Real-time grid stability monitoring and ancillary service management")
st.divider()

# ─── Load Data ────────────────────────────────────────────────
freq_data = get_grid_frequency()
voltage_data = get_voltage_status()
reserve_data = get_spinning_reserve()
services = get_ancillary_services_status()
events = generate_grid_events(10)
freq_history = get_frequency_history(4)
revenue = get_ancillary_revenue()

# ─── Grid Status Banner ───────────────────────────────────────
overall_status = "NORMAL"
overall_color = config.COLOR_NORMAL

if (freq_data["status"] == "CRITICAL" or
        voltage_data["status"] == "CRITICAL"):
    overall_status = "CRITICAL — IMMEDIATE ACTION REQUIRED"
    overall_color = config.COLOR_CRITICAL
elif (freq_data["status"] == "WARNING" or
        voltage_data["status"] == "WARNING"):
    overall_status = "WARNING — MONITOR CLOSELY"
    overall_color = config.COLOR_WARNING

st.markdown(f"""
<div style="background-color:{overall_color}; padding:15px;
border-radius:10px; color:white; text-align:center;
font-size:20px; font-weight:bold;">
GRID STATUS: {overall_status}
</div>
""", unsafe_allow_html=True)

st.markdown("")

# ─── KPI Cards ────────────────────────────────────────────────
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="Grid Frequency",
        value=f"{freq_data['frequency_hz']} Hz",
        delta=f"{freq_data['deviation_hz']:+.3f} Hz deviation",
        delta_color="inverse" if abs(
            freq_data['deviation_hz']) > 0.1 else "normal"
    )

with col2:
    st.metric(
        label="Voltage at PCC",
        value=f"{voltage_data['voltage_v']} V",
        delta=f"{voltage_data['deviation_pct']:+.2f}% deviation",
        delta_color="inverse" if abs(
            voltage_data['deviation_pct']) > 3 else "normal"
    )

with col3:
    st.metric(
        label="Spinning Reserve",
        value=f"{reserve_data['available_kw']} kW",
        delta=reserve_data['status']
    )

with col4:
    total_ancillary_revenue = sum(revenue.values())
    st.metric(
        label="Monthly Ancillary Revenue",
        value=f"CAD {total_ancillary_revenue:,.0f}",
        delta="from grid stability services"
    )

st.divider()

# ─── Frequency and Voltage Status ────────────────────────────
st.subheader("Grid Frequency and Voltage Status")

col1, col2 = st.columns(2)

with col1:
    st.markdown("**Grid Frequency Monitor**")

    freq_color = freq_data["color"]
    st.markdown(f"""
    <div style="background-color:{freq_color}; padding:20px;
    border-radius:10px; color:white; text-align:center;">
    <h2>{freq_data['frequency_hz']} Hz</h2>
    <p>{freq_data['message']}</p>
    <p>Target: {config.GRID_FREQUENCY_HZ} Hz</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("")

    fig_freq = go.Figure()

    fig_freq.add_trace(go.Scatter(
        x=freq_history["timestamps"],
        y=freq_history["frequencies"],
        name='Frequency (Hz)',
        line=dict(color=config.COLOR_WIND, width=2),
        fill='tozeroy',
        fillcolor='rgba(66,164,245,0.1)'
    ))

    fig_freq.add_hline(
        y=config.GRID_FREQUENCY_HZ,
        line_dash="dash",
        line_color=config.COLOR_NORMAL,
        annotation_text="Target: 60.00 Hz"
    )

    fig_freq.add_hline(
        y=config.GRID_FREQUENCY_HZ + config.FREQUENCY_WARNING,
        line_dash="dot",
        line_color=config.COLOR_WARNING,
        annotation_text="Warning Limit"
    )

    fig_freq.add_hline(
        y=config.GRID_FREQUENCY_HZ - config.FREQUENCY_WARNING,
        line_dash="dot",
        line_color=config.COLOR_WARNING
    )

    fig_freq.update_layout(
        height=250,
        xaxis_title="Time",
        yaxis_title="Frequency (Hz)",
        plot_bgcolor='white',
        yaxis=dict(
            gridcolor='#f0f0f0',
            range=[59.5, 60.5]
        ),
        showlegend=False
    )

    st.plotly_chart(fig_freq, use_container_width=True)
    st.caption("Last 4 hours of grid frequency. Green dashed = target. Orange dotted = warning limits.")

with col2:
    st.markdown("**Voltage Monitor at Point of Common Coupling**")

    volt_color = voltage_data["color"]
    st.markdown(f"""
    <div style="background-color:{volt_color}; padding:20px;
    border-radius:10px; color:white; text-align:center;">
    <h2>{voltage_data['voltage_v']} V</h2>
    <p>{voltage_data['message']}</p>
    <p>Nominal: {voltage_data['nominal_v']} V</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("")

    nominal = config.VOLTAGE_NOMINAL_V
    warning_high = nominal * (1 + config.VOLTAGE_WARNING_PCT)
    warning_low = nominal * (1 - config.VOLTAGE_WARNING_PCT)
    critical_high = nominal * (1 + config.VOLTAGE_CRITICAL_PCT)
    critical_low = nominal * (1 - config.VOLTAGE_CRITICAL_PCT)

    fig_volt = go.Figure()

    fig_volt.add_hrect(
        y0=warning_low, y1=warning_high,
        fillcolor="rgba(0,204,68,0.1)",
        line_width=0,
        annotation_text="Normal Range"
    )

    fig_volt.add_trace(go.Indicator(
        mode="gauge+number",
        value=voltage_data['voltage_v'],
        domain={'x': [0, 1], 'y': [0, 1]},
        gauge={
            'axis': {
                'range': [critical_low, critical_high],
                'tickwidth': 1
            },
            'bar': {'color': volt_color},
            'steps': [
                {'range': [critical_low, warning_low],
                 'color': '#ffcccc'},
                {'range': [warning_low, warning_high],
                 'color': '#ccffcc'},
                {'range': [warning_high, critical_high],
                 'color': '#ffcccc'}
            ],
            'threshold': {
                'line': {'color': "black", 'width': 4},
                'thickness': 0.75,
                'value': nominal
            }
        }
    ))

    fig_volt.update_layout(height=300)
    st.plotly_chart(fig_volt, use_container_width=True)
    st.caption("Green zone = normal operating range. Red zones = warning and critical limits.")

st.divider()

# ─── Ancillary Services Status ────────────────────────────────
st.subheader("Ancillary Services Status")

cols = st.columns(4)

for i, service in enumerate(services):
    with cols[i]:
        st.markdown(f"""
        <div style="background-color:{service['color']};
        padding:15px; border-radius:10px; color:white;
        text-align:center; height:150px;">
        <h4>{service['name']}</h4>
        <h3>{service['status']}</h3>
        <p>{service['capacity_kw']} kW</p>
        <p>CAD {service['revenue_today_cad']} today</p>
        </div>
        """, unsafe_allow_html=True)

st.markdown("")
st.divider()

# ─── Ancillary Revenue Chart ──────────────────────────────────
st.subheader("Monthly Ancillary Services Revenue")

col1, col2 = st.columns(2)

with col1:
    fig_rev = go.Figure(data=[go.Bar(
        x=list(revenue.keys()),
        y=list(revenue.values()),
        marker_color=[
            config.COLOR_NORMAL,
            config.COLOR_WIND,
            config.COLOR_BESS,
            config.COLOR_SOLAR
        ]
    )])

    fig_rev.update_layout(
        height=300,
        xaxis_title="Service Type",
        yaxis_title="Monthly Revenue (CAD)",
        plot_bgcolor='white',
        yaxis=dict(gridcolor='#f0f0f0'),
        xaxis=dict(
            ticktext=[
                'Frequency\nRegulation',
                'Voltage\nSupport',
                'Spinning\nReserve',
                'Black\nStart'
            ],
            tickvals=list(revenue.keys())
        )
    )

    st.plotly_chart(fig_rev, use_container_width=True)

with col2:
    st.markdown("### Monthly Revenue Breakdown")
    st.markdown("")

    for service_name, amount in revenue.items():
        clean_name = service_name.replace('_cad', '').replace('_', ' ').title()
        st.metric(
            label=clean_name,
            value=f"CAD {amount:,.0f}"
        )

    st.metric(
        label="Total Monthly Ancillary Revenue",
        value=f"CAD {sum(revenue.values()):,.0f}"
    )

st.divider()

# ─── Grid Event Log ───────────────────────────────────────────
st.subheader("Grid Event Log — Last 24 Hours")

events_df = pd.DataFrame(events)

st.dataframe(
    events_df,
    use_container_width=True,
    hide_index=True
)

col1, col2 = st.columns(2)

with col1:
    csv = events_df.to_csv(index=False)
    st.download_button(
        label="Download Event Log (CSV)",
        data=csv,
        file_name="grid_event_log.csv",
        mime="text/csv"
    )

with col2:
    st.caption("Event log required for NERC CIP compliance reporting. Retain for minimum 2 years.")

st.divider()

# ─── Plain English Summary ────────────────────────────────────
st.subheader("Ancillary Services Summary in Plain English")

st.info(f"""
Your grid connection is currently operating in
{freq_data['status']} condition. The grid frequency
is {freq_data['frequency_hz']} Hz which is
{abs(freq_data['deviation_hz']):.3f} Hz
{'above' if freq_data['deviation_hz'] > 0 else 'below'}
the target of {config.GRID_FREQUENCY_HZ} Hz.

Your voltage at the point of common coupling is
{voltage_data['voltage_v']} V which is
{abs(voltage_data['deviation_pct']):.2f}%
{'above' if voltage_data['deviation_pct'] > 0 else 'below'}
the nominal {voltage_data['nominal_v']} V.

You have {reserve_data['available_kw']} kW of spinning
reserve available which is {reserve_data['status']}
with NERC BAL-002 requirements.

Your four ancillary services are earning a combined
CAD {sum(revenue.values()):,.0f} per month from
the grid operator — completely automatically with
no additional work required from your team.

The grid event log shows {len(events)} events in the
last 24 hours. All events have been automatically
resolved and logged for NERC CIP compliance reporting.
""")

st.caption("GreenGrid AI v1.0 — Ancillary services monitoring per NERC CIP and IEEE 1547 standards")

