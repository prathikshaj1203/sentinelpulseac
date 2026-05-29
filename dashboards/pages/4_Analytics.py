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

# Check if running in Hugging Face or Cloud container, otherwise default to local development endpoint
space_id = os.getenv("SPACE_ID")
if space_id:
    # Convert 'Owner/SpaceName' to 'owner-spacename' for HF subdomains
    subdomain = "-".join(space_id.lower().split("/"))
    grafana_url = f"https://{subdomain}.hf.space/grafana/d/hvac_telemetry_dash?kiosk&orgId=1"
elif os.getenv("KAFKA_BOOTSTRAP_SERVERS"):
    # Generic cloud container setup
    grafana_url = "/grafana/d/hvac_telemetry_dash?kiosk&orgId=1"
else:
    grafana_url = "http://localhost:3000/d/hvac_telemetry_dash?kiosk&orgId=1"

components.iframe(
    grafana_url,
    height=1000,
    scrolling=True
)