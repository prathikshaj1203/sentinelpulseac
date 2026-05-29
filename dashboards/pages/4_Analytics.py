import streamlit as st
import streamlit.components.v1 as components
from utils.ui import init_page, page_header

# =========================================
# PAGE CONFIG & AUTH (Must be first)
# =========================================
init_page("SentinelPulse AI - Analytics", required_role="ADMIN")

# =========================================
# PAGE HEADER
# =========================================
page_header("Industrial Analytics Center", "Real-time Grafana observability dashboard")

# =========================================
# EMBED GRAFANA (Iframe)
# =========================================
grafana_url = "http://localhost:3000/d/hvac_telemetry_dash?kiosk&orgId=1"

components.iframe(
    grafana_url,
    height=1000,
    scrolling=True
)