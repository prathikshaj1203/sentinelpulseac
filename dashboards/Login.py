# ───────────────────────────────────────────────────
# PROJECT   : SentinelPulse AI – Real-Time Predictive Maintenance System for Industrial Air Compressors
# FILE      : Login.py
# AUTHOR    : PRATHIKSHA J
# INTERN ID : SIT067
# DIVISION  : Software & AI Division – Stacia Corp
# MENTOR    : Mr. Lakshman P V (Chief Operational Officer)
# DATE      : 29-05-2026
# VERSION   : v1.0
# ───────────────────────────────────────────────────
# DESCRIPTION:
# Entrypoint and authentication page for the SentinelPulse Streamlit dashboard application.
# ───────────────────────────────────────────────────
# DEPENDENCIES:
# streamlit, dashboards.utils.ui, dashboards.utils.auth
# ───────────────────────────────────────────────────
# USAGE:
# streamlit run dashboards/Login.py
# ═══════════════════════════════════════════════════

import streamlit as st
from utils.ui import load_css
from utils.auth import authenticate

# =========================================
# PAGE SETUP (Must be the very first Streamlit call)
# =========================================
st.set_page_config(
    page_title="SentinelPulse AI - Login",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Load futuristic purple glow styling
load_css()

# Hide Sidebar on Login Page and inject compact styles
st.markdown("""
<style>
[data-testid="stSidebar"] {
    display: none !important;
}
/* Reduce vertical gap between elements inside containers */
[data-testid="stVerticalBlock"] {
    gap: 6px !important;
}
/* Compact Input Boxes */
div[data-testid="stTextInput"] > div > div > input {
    padding-top: 4px !important;
    padding-bottom: 4px !important;
    height: 38px !important;
    font-size: 14px !important;
}
/* Compact Buttons */
div[data-testid="stButton"] button {
    padding-top: 4px !important;
    padding-bottom: 4px !important;
    height: 38px !important;
    font-size: 14px !important;
}
/* Compact Tabs */
button[data-baseweb="tab"] {
    padding-top: 4px !important;
    padding-bottom: 4px !important;
    font-size: 14px !important;
}
</style>
""", unsafe_allow_html=True)

# =========================================
# SESSION STATE INITIALIZATION
# =========================================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "role" not in st.session_state:
    st.session_state.role = ""

# =========================================
# LOGIN UI & LAYOUT
# =========================================

# Render clean text header
st.markdown("""
<div style="text-align: center; margin-top: -10px; margin-bottom: 25px;">
    <h1 class="main-title" style="font-size: 42px; text-align: center; margin-bottom: 8px; font-weight: 800; color: #FFFFFF; text-shadow: 0 0 15px rgba(168, 85, 247, 0.5);">SentinelPulse AI</h1>
    <p class="sub-title" style="text-align: center; font-size: 16px; color: #A855F7; letter-spacing: 1px; font-weight: 500;">Industrial Predictive Maintenance Platform</p>
</div>
""", unsafe_allow_html=True)

# Login/Signup forms centered below the logo
left, center, right = st.columns([1.1, 1.0, 1.1])

with center:
    tab1, tab2 = st.tabs(["Login", "Register Technician"])

    with tab1:
        username = st.text_input("Username", key="login_user")
        password = st.text_input("Password", type="password", key="login_pass")
        login_button = st.button("Login", key="login_btn", use_container_width=True)

        if login_button:
            if not username or not password:
                st.error("Please fill in all fields.")
            else:
                user = authenticate(username, password)
                if user:
                    role_upper = user[1].upper()
                    if role_upper not in ["ADMIN", "TECHNICIAN"]:
                        st.error("Access Denied: Authorized role required.")
                    else:
                        st.session_state.logged_in = True
                        st.session_state.username = user[0]
                        st.session_state.role = user[1]
                        st.session_state.full_name = user[2]
                        st.session_state.department = user[3]
                        
                        st.success(f"Welcome {user[2]}")
                        if role_upper == "ADMIN":
                            st.switch_page("pages/0_Home.py")
                        else:
                            st.switch_page("pages/1_Sensor_Monitoring.py")
                else:
                    st.error("Invalid username or password")

    with tab2:
        col_row1_left, col_row1_right = st.columns(2)
        with col_row1_left:
            reg_fullname = st.text_input("Full Name", key="reg_fullname")
        with col_row1_right:
            reg_username = st.text_input("Username", key="reg_username")

        col_row2_left, col_row2_right = st.columns(2)
        with col_row2_left:
            reg_password = st.text_input("Password", type="password", key="reg_password")
        with col_row2_right:
            reg_confirm = st.text_input("Confirm Password", type="password", key="reg_confirm")

        signup_button = st.button("Sign Up", key="reg_btn", use_container_width=True)

        if signup_button:
            if not reg_fullname or not reg_username or not reg_password or not reg_confirm:
                st.error("All fields are required.")
            elif reg_password != reg_confirm:
                st.error("Passwords do not match.")
            elif len(reg_password) < 4:
                st.error("Password must be at least 4 characters.")
            else:
                from utils.auth import username_exists, register_user
                if username_exists(reg_username):
                    st.error("Username is already taken.")
                else:
                    register_user(reg_username, reg_password, reg_fullname)
                    st.success("Registration successful! You can now log in.")