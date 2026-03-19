
import streamlit as st

st.set_page_config(
    page_title="GreenGrid AI",
    layout="wide"
)

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

# Password Protection
def check_password():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if not st.session_state.authenticated:
        st.markdown(
            '<h1 style="color:#00cc44;">GreenGrid AI</h1>',
            unsafe_allow_html=True
        )
        st.markdown("Smart Distributed Energy Resource Management")
        st.divider()
        st.subheader("Demo Access Required")
        st.info("""
        This is a proprietary demo application.
        Please enter the access password to continue.
        To request access contact:
        **aamirqadeer.ca@gmail.com**
        """)

        password = st.text_input(
            "Enter Demo Password",
            type="password"
        )

        if st.button("Access Demo", type="primary"):
            import os
            correct_password = os.getenv(
                "DEMO_PASSWORD", "GreenGrid2026"
            )
            if password == correct_password:
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("Incorrect password. Please try again.")
                st.info("""
                To request demo access please contact:
                aamirqadeer.ca@gmail.com
                """)
        return False
    return True

if not check_password():
    st.stop()

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
st.caption("GreenGrid AI v1.0 — © 2026 Aamir Qadeer — AI & Energy Engineer — All Rights Reserved")

