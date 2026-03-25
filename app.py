
import streamlit as st
import base64
import os

st.set_page_config(
    page_title="GreenGrid AI",
    layout="wide"
)

# --- Encode image to base64 for embedding ----------------------------------
def get_image_base64(image_path):
    with open(image_path, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

image_path = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "For_greenGrid.jpg"
)

try:
    img_b64 = get_image_base64(image_path)
    img_html = f'<img src="data:image/jpeg;base64,{img_b64}" style="width:100%; max-height:320px; object-fit:cover; border-radius:14px; box-shadow: 0 4px 16px rgba(0,0,0,0.3);">'
except:
    img_html = ""

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
    margin-bottom: 10px;
}
</style>
""", unsafe_allow_html=True)

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

*Unauthorized copying prohibited*
""")

# --- Main page header ------------------------------------------------------
st.markdown('<p class="main-header">GreenGrid AI</p>',
            unsafe_allow_html=True)
st.markdown('<p class="sub-header">Smart Distributed Energy Resource Management System: Engineered for North American Enterprise.</p>',
            unsafe_allow_html=True)

# --- Image below title -----------------------------------------------------
st.markdown(
    f'<div style="margin-top:15px; margin-bottom:10px;">{img_html}</div>',
    unsafe_allow_html=True
)

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
st.caption("GreenGrid AI v1.0 — © 2026 Aamir Qadeer — AI & Energy Engineer — All Rights Reserved")

