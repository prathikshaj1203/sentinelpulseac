# ───────────────────────────────────────────────────
# PROJECT   : SentinelPulse AI – Real-Time Predictive Maintenance System for Industrial Air Compressors
# FILE      : 1_Sensor_Monitoring.py
# AUTHOR    : PRATHIKSHA J
# INTERN ID : SIT067
# DIVISION  : Software & AI Division – Stacia Corp
# MENTOR    : Mr. Lakshman P V (Chief Operational Officer)
# DATE      : 29-05-2026
# VERSION   : v1.0
# ───────────────────────────────────────────────────
# DESCRIPTION:
# Real-time telemetry trend analysis panel rendering live sensor signals via interactive charts.
# ───────────────────────────────────────────────────
# DEPENDENCIES:
# streamlit, pandas, plotly.express, dashboards.utils.ui, dashboards.utils.db
# ───────────────────────────────────────────────────
# USAGE:
# Accessed via Streamlit sidebar navigation.
# ═══════════════════════════════════════════════════

import streamlit as st
import pandas as pd
import plotly.express as px
from utils.ui import init_page, page_header
from utils.db import fetch_data

# =========================================
# PAGE SETUP & AUTH (Must be first)
# =========================================
init_page("SentinelPulse AI - Sensor Monitoring", required_role=["ADMIN", "TECHNICIAN"])

# =========================================
# FETCH TELEMETRY
# =========================================
df = fetch_data("SELECT * FROM telemetry_data ORDER BY timestamp DESC LIMIT 300")

# =========================================
# PAGE HEADER
# =========================================
page_header("Live Sensor Monitoring", "Real-time industrial HVAC telemetry monitoring")

if df.empty:
    st.info("No telemetry data streams available.")
    st.stop()

# =========================================
# MACHINE SELECTOR
# =========================================
machines = df["machine_id"].unique()
selected_machine = st.selectbox("Select Machine Asset", machines)

machine_df = df[df["machine_id"] == selected_machine]

if machine_df.empty:
    st.warning("No data found for the selected machine.")
    st.stop()

latest = machine_df.iloc[0]

# =========================================
# LIVE STATUS METRICS
# =========================================
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.metric("Temperature", f"{latest['temperature']:.1f} °C")
with c2:
    st.metric("Vibration Level", f"{latest['vibration']:.2f}")
with c3:
    st.metric("Failure Probability", f"{latest['failure_probability']:.1f}%")
with c4:
    st.metric("Asset Risk Level", latest["risk_level"])

st.markdown("---")

# =========================================
# PLOTLY CHART FACTORY
# =========================================
def render_trend_chart(data, y_field, title_label, line_color="#A855F7"):
    fig = px.line(
        data.sort_values("timestamp"),
        x="timestamp",
        y=y_field,
        title=title_label
    )
    fig.update_traces(line_color=line_color, line_width=2.5)
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=10, r=10, t=40, b=10),
        xaxis=dict(showgrid=False, color="#9CA3AF"),
        yaxis=dict(showgrid=True, gridcolor="rgba(168, 85, 247, 0.1)", color="#9CA3AF")
    )
    st.plotly_chart(fig, use_container_width=True)

# =========================================
# LIVE TRENDS
# =========================================
st.subheader("Live Telemetry Trends")

col_left, col_right = st.columns(2)
with col_left:
    render_trend_chart(machine_df, "temperature", "Temperature Trend (°C)", "#A855F7")
with col_right:
    render_trend_chart(machine_df, "vibration", "Vibration Trend (RMS)", "#6366F1")

st.markdown("###")
render_trend_chart(machine_df, "failure_probability", "AI Failure Probability Trend (%)", "#F43F5E")

st.markdown("---")

# =========================================
# LATEST DATA LOG
# =========================================
st.subheader("Latest Telemetry Logs (20 Records)")
st.dataframe(machine_df.head(20), width='stretch', hide_index=True)