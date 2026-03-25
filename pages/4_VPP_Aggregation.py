

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from modules.aggregator import (
    get_site_status,
    get_vpp_aggregation,
    get_market_data,
    get_revenue_data,
    get_bid_recommendation
)
import config

# ─── Page Configuration ──────────────────────────────────────
st.set_page_config(page_title="VPP Aggregation", layout="wide")

st.markdown('<h1 style="color:#00cc44;">VPP Aggregation</h1>',
            unsafe_allow_html=True)
st.markdown("Virtual Power Plant — Five sites aggregated for Canadian energy market participation")
st.divider()

# ─── Load Data ────────────────────────────────────────────────
with st.spinner("Loading VPP data from all sites..."):
    site_statuses = get_site_status()
    vpp_data = get_vpp_aggregation(site_statuses)
    market_data = get_market_data()
    revenue_data = get_revenue_data()
    bid_rec = get_bid_recommendation(vpp_data, market_data)

# ─── KPI Cards ────────────────────────────────────────────────
st.subheader("VPP Summary — All Sites Combined")

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric(
        label="Total VPP Capacity",
        value=f"{vpp_data['available_capacity_kw']:.0f} kW",
        delta=f"{vpp_data['total_sites']} sites online"
    )

with col2:
    st.metric(
        label="Total Solar Output",
        value=f"{vpp_data['total_solar_kw']:.0f} kW",
        delta=f"of {vpp_data['total_solar_capacity_kw']} kW capacity"
    )

with col3:
    st.metric(
        label="Total Wind Output",
        value=f"{vpp_data['total_wind_kw']:.0f} kW",
        delta=f"of {vpp_data['total_wind_capacity_kw']} kW capacity"
    )

with col4:
    st.metric(
        label="Average BESS SOC",
        value=f"{vpp_data['avg_bess_soc_pct']:.0f}%",
        delta=f"{vpp_data['dispatchable_kw']:.0f} kW dispatchable"
    )

with col5:
    st.metric(
        label="Today's VPP Revenue",
        value=f"CAD {revenue_data['daily_total_cad']}",
        delta=f"CAD {revenue_data['monthly_total_cad']:,.0f} projected monthly"
    )

st.divider()

# ─── Market Status ────────────────────────────────────────────
st.subheader("Energy Market Status")

col1, col2, col3 = st.columns(3)

with col1:
    ieso_color = (config.COLOR_CRITICAL
                  if market_data['ieso_price_mwh'] > 100
                  else config.COLOR_WARNING
                  if market_data['ieso_price_mwh'] > 70
                  else config.COLOR_NORMAL)

    st.markdown(f"""
    <div style="background-color:{ieso_color}; padding:15px;
    border-radius:10px; color:white; text-align:center;">
    <h3>IESO Ontario</h3>
    <h2>CAD {market_data['ieso_price_mwh']}/MWh</h2>
    <p>Market Status: {market_data['market_status']}</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    aeso_color = (config.COLOR_CRITICAL
                  if market_data['aeso_price_mwh'] > 100
                  else config.COLOR_WARNING
                  if market_data['aeso_price_mwh'] > 70
                  else config.COLOR_NORMAL)

    st.markdown(f"""
    <div style="background-color:{aeso_color}; padding:15px;
    border-radius:10px; color:white; text-align:center;">
    <h3>AESO Alberta</h3>
    <h2>CAD {market_data['aeso_price_mwh']:.0f}/MWh</h2>
    <p>Next Peak: {market_data['next_peak_window']}</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    urgency_color = (config.COLOR_CRITICAL
                     if bid_rec['urgency'] == "HIGH"
                     else config.COLOR_WARNING
                     if bid_rec['urgency'] == "MEDIUM"
                     else config.COLOR_NORMAL)

    st.markdown(f"""
    <div style="background-color:{urgency_color}; padding:15px;
    border-radius:10px; color:white; text-align:center;">
    <h3>Bid Recommendation</h3>
    <h4>{bid_rec['recommendation']}</h4>
    <p>Bid: {bid_rec['bid_quantity_kw']:.0f} kW —
    Expected: CAD {bid_rec['expected_revenue_cad']}</p>
    </div>
    """, unsafe_allow_html=True)

st.divider()

# ─── Site Map ─────────────────────────────────────────────────
st.subheader("VPP Site Locations — Canada")

map_data = pd.DataFrame([{
    "name": s["name"],
    "lat": s["lat"],
    "lon": s["lon"],
    "status": s["status"],
    "solar_kw": s["solar_kw"],
    "wind_kw": s["wind_kw"],
    "bess_soc_pct": s["bess_soc_pct"],
    "grid_operator": s["grid_operator"],
    "size": 20
} for s in site_statuses])

color_map = {
    "Online": "#00cc44",
    "Warning": "#ff8c00",
    "Offline": "#ff0000"
}

fig_map = px.scatter_mapbox(
    map_data,
    lat="lat",
    lon="lon",
    color="status",
    color_discrete_map=color_map,
    size="size",
    hover_name="name",
    hover_data={
        "solar_kw": True,
        "wind_kw": True,
        "bess_soc_pct": True,
        "grid_operator": True,
        "status": True,
        "size": False,
        "lat": False,
        "lon": False
    },
    zoom=3,
    center={"lat": 50.0, "lon": -95.0},
    mapbox_style="open-street-map",
    height=450,
    title="VPP Site Locations"
)

fig_map.update_layout(
    margin=dict(l=0, r=0, t=30, b=0)
)

st.plotly_chart(fig_map, use_container_width=True)
st.caption("Green = Online. Orange = Warning. Red = Offline. Click any site for details.")

st.divider()

# ─── Site Status Table ────────────────────────────────────────
st.subheader("Individual Site Status")

site_df = pd.DataFrame([{
    "Site Name": s["name"],
    "Location": s["location"],
    "Grid": s["grid_operator"],
    "Solar (kW)": s["solar_kw"],
    "Wind (kW)": s["wind_kw"],
    "BESS SOC (%)": s["bess_soc_pct"],
    "Load (kW)": s["load_kw"],
    "Status": s["status"]
} for s in site_statuses])

st.dataframe(
    site_df,
    use_container_width=True,
    hide_index=True
)

st.divider()

# ─── Revenue Dashboard ────────────────────────────────────────
st.subheader("VPP Revenue Dashboard")

col1, col2 = st.columns(2)

with col1:
    fig_rev = go.Figure(data=[go.Pie(
        labels=[
            'Energy Market',
            'Demand Response',
            'Ancillary Services'
        ],
        values=[
            revenue_data['daily_energy_cad'],
            revenue_data['daily_dr_cad'],
            revenue_data['daily_ancillary_cad']
        ],
        hole=0.4,
        marker=dict(colors=[
            config.COLOR_SOLAR,
            config.COLOR_WIND,
            config.COLOR_BESS
        ])
    )])

    fig_rev.update_layout(
        title="Today's Revenue by Source (CAD)",
        height=350,
        showlegend=True
    )

    st.plotly_chart(fig_rev, use_container_width=True)

with col2:
    st.markdown("### Revenue Summary")
    st.markdown("")

    st.metric(
        label="Energy Market Revenue",
        value=f"CAD {revenue_data['daily_energy_cad']}"
    )
    st.metric(
        label="Demand Response Revenue",
        value=f"CAD {revenue_data['daily_dr_cad']}"
    )
    st.metric(
        label="Ancillary Services Revenue",
        value=f"CAD {revenue_data['daily_ancillary_cad']}"
    )
    st.metric(
        label="Total Daily Revenue",
        value=f"CAD {revenue_data['daily_total_cad']}"
    )
    st.metric(
        label="Projected Monthly Revenue",
        value=f"CAD {revenue_data['monthly_total_cad']:,.0f}"
    )
    st.metric(
        label="Projected Annual Revenue",
        value=f"CAD {revenue_data['annual_total_cad']:,.0f}"
    )

st.divider()

# ─── Capacity Breakdown Chart ─────────────────────────────────
st.subheader("VPP Capacity Breakdown")

fig_cap = go.Figure()

site_names = [s["name"].split()[0] for s in site_statuses]

fig_cap.add_trace(go.Bar(
    name='Solar Output (kW)',
    x=site_names,
    y=[s["solar_kw"] for s in site_statuses],
    marker_color=config.COLOR_SOLAR
))

fig_cap.add_trace(go.Bar(
    name='Wind Output (kW)',
    x=site_names,
    y=[s["wind_kw"] for s in site_statuses],
    marker_color=config.COLOR_WIND
))

fig_cap.add_trace(go.Bar(
    name='BESS SOC (%)',
    x=site_names,
    y=[s["bess_soc_pct"] for s in site_statuses],
    marker_color=config.COLOR_BESS
))

fig_cap.update_layout(
    height=config.CHART_HEIGHT,
    barmode='group',
    xaxis_title="Site",
    yaxis_title="Output (kW) / SOC (%)",
    hovermode='x unified',
    plot_bgcolor='white',
    yaxis=dict(gridcolor='#f0f0f0'),
    legend=dict(orientation="h", yanchor="bottom", y=1.02)
)

st.plotly_chart(fig_cap, use_container_width=True)

st.divider()

# ─── Plain English Summary ────────────────────────────────────
st.subheader("VPP Summary in Plain English")

st.success(f"""
Your Virtual Power Plant currently combines
{vpp_data['total_sites']} sites with a total available
capacity of {vpp_data['available_capacity_kw']:.0f} kW.

Your {vpp_data['ieso_sites']} Ontario sites participate
in the IESO market where electricity is currently
trading at CAD {market_data['ieso_price_mwh']}/MWh.
Your {vpp_data['aeso_sites']} Alberta sites participate
in the AESO market at CAD {market_data['aeso_price_mwh']:.0f}/MWh.

Today your VPP has already earned CAD {revenue_data['daily_total_cad']}
from energy market sales demand response and ancillary services.
At this rate your projected monthly VPP revenue is
CAD {revenue_data['monthly_total_cad']:,.0f} and annual revenue
is CAD {revenue_data['annual_total_cad']:,.0f}.

Current recommendation: {bid_rec['recommendation']}
""")

st.caption("GreenGrid AI v1.0 — VPP powered by aggregated DER assets across Ontario and Alberta")


