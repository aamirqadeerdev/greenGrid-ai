

import streamlit as st
import base64
import os

st.set_page_config(
    page_title="GreenGrid AI",
    layout="wide"
)

# ---------------------------------------------------------------------------
# PASSWORD PROTECTION
# ---------------------------------------------------------------------------
def check_password():
    def password_entered():
        if st.session_state["password"] == st.secrets["APP_PASSWORD"]:
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    if st.session_state.get("password_correct", False):
        return True

    # --- Login UI ---
    st.markdown("""
    <style>
    .login-header {
        font-size: 28px;
        font-weight: bold;
        color: #00cc44;
        margin-bottom: 4px;
    }
    .login-sub {
        font-size: 14px;
        color: #888888;
        margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.markdown('<p class="login-header">🌿 GreenGrid AI</p>', unsafe_allow_html=True)
        st.markdown('<p class="login-sub">Smart Distributed Energy Resource Management System</p>', unsafe_allow_html=True)
        st.text_input("🔒 Enter Password", type="password", on_change=password_entered, key="password")
        if "password_correct" in st.session_state and not st.session_state["password_correct"]:
            st.error("❌ Incorrect password. Please try again.")
        st.caption("Authorized users only. © 2026 Aamir Qadeer")

    return False


if not check_password():
    st.stop()

# ---------------------------------------------------------------------------
# MAIN APP (only rendered after correct password)
# ---------------------------------------------------------------------------

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


