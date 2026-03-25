

import streamlit as st
import base64
import os

def hide_running_man():
    st.markdown("""
    <style>
    [data-testid="stStatusWidget"] { display: none !important; }
    </style>
    """, unsafe_allow_html=True)


def show_logo_top_right():
    """
    Call this at the top of any page to show the GreenGrid image
    in the upper right corner.
    """
    image_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "For_greenGrid.jpg"
    )
    try:
        with open(image_path, "rb") as f:
            img_b64 = base64.b64encode(f.read()).decode()
        st.markdown(
            f"""
            <div style="position:fixed; top:60px; right:20px; z-index:999;">
                <img src="data:image/jpeg;base64,{img_b64}"
                     style="width:180px; border-radius:12px;
                            box-shadow: 0 4px 12px rgba(0,0,0,0.3);
                            opacity:0.92;">
            </div>
            """,
            unsafe_allow_html=True
        )
    except:
        pass
