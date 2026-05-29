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

import os

# Check if a custom Grafana URL is provided (e.g. hosted in the cloud)
grafana_url = os.getenv("GRAFANA_URL")

if grafana_url:
    components.iframe(
        grafana_url,
        height=1000,
        scrolling=True
    )
else:
    st.markdown("""
    <div style="background: rgba(147, 51, 234, 0.05); border: 1px solid rgba(147, 51, 234, 0.2); border-radius: 12px; padding: 30px; text-align: center; margin-top: 20px; box-shadow: 0 4px 30px rgba(147, 51, 234, 0.05); backdrop-filter: blur(5px);">
        <h3 style="color: #c084fc; margin-top: 0; margin-bottom: 12px; font-weight: 700; font-size: 22px;">📊 Grafana Observability Portal</h3>
        <p style="color: #cbd5e1; font-size: 15px; max-width: 600px; margin: 0 auto 20px auto; line-height: 1.6;">
            By default, Grafana is configured to run locally on your host machine to visualize real-time Kafka metrics.
        </p>
        
        <div style="background: rgba(15, 23, 42, 0.6); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 8px; padding: 12px 24px; display: inline-block; text-align: left; margin-bottom: 24px;">
            <span style="color: #94a3b8; font-size: 12px; text-transform: uppercase; font-weight: bold; display: block; margin-bottom: 4px;">Local Port Access</span>
            <code style="color: #38bdf8; font-family: monospace; font-size: 15px; font-weight: 600;">http://localhost:3000</code>
        </div>
        
        <p style="color: #94a3b8; font-size: 13px; max-width: 500px; margin: 0 auto; line-height: 1.5;">
            To view this dashboard in your 24/7 cloud deployment, spin up a Grafana instance in the cloud and add your public URL as a <b>GRAFANA_URL</b> environment variable in your Hugging Face Space settings.
        </p>
    </div>
    """, unsafe_allow_html=True)