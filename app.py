

import streamlit as st

# Copyright watermark in sidebar
st.sidebar.markdown("""
---
**GreenGrid AI v1.0**

Proprietary Software

© 2026 Aamir Qadeer

AI & Energy Engineer

aamirqadeer.ca@gmail.com

---
*All Rights Reserved*

*Unauthorized copying or*

*distribution prohibited*
""")


st.set_page_config(
    page_title="GreenGrid AI",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
.main-header {
    font-size: 32px;
    font-weight: bold;
    color: #00cc44;
    margin-bottom: 0px;
}
.sub-header {
    font-size: 16px;
    color: #888888;
    margin-bottom: 20px;
}
.kpi-card {
    background-color: #f8f9fa;
    border-radius: 10px;
    padding: 15px;
    border-left: 4px solid #00cc44;
}
</style>
""", unsafe_allow_html=True)

# Main page header
st.markdown('<p class="main-header">GreenGrid AI</p>',
            unsafe_allow_html=True)
st.markdown('<p class="sub-header">Smart Distributed Energy Resource Management for Small Canadian Operators</p>',
            unsafe_allow_html=True)
st.divider()

# Welcome message
col1, col2, col3 = st.columns(3)

with col1:
    st.info("""
    **Navigate Using the Sidebar**
    
    Use the left sidebar to access all
    six modules of GreenGrid AI.
    """)

with col2:
    st.success("""
    **System Status: Online**
    
    All DER resources connected.
    Simulated data active.
    """)

with col3:
    st.warning("""
    **Demo Mode Active**
    
    Using simulated data for demonstration.
    Contact us to connect real DER hardware.
    """)

st.divider()

# Quick overview
st.subheader("What GreenGrid AI Does")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown("""
    **Forecasting**
    
    Predicts solar, wind, and
    load for next 24-48 hours
    using weather data and ML.
    """)

with col2:
    st.markdown("""
    **Optimization**
    
    Schedules battery charging
    and EV charging to minimize
    your electricity costs.
    """)

with col3:
    st.markdown("""
    **VPP Aggregation**
    
    Groups your resources with
    other sites to participate
    in Canadian energy markets.
    """)

with col4:
    st.markdown("""
    **Ancillary Services**
    
    Monitors grid frequency
    and voltage to keep your
    connection stable and safe.
    """)

st.divider()
st.caption("GreenGrid AI v1.0 — Built by Aamir Qadeer — AI & Energy Engineer — Available for Canadian remote opportunities")
