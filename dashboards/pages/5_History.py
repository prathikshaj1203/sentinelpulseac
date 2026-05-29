# ───────────────────────────────────────────────────
# PROJECT   : SentinelPulse AI – Real-Time Predictive Maintenance System for Industrial Air Compressors
# FILE      : 5_History.py
# AUTHOR    : PRATHIKSHA J
# INTERN ID : SIT067
# DIVISION  : Software & AI Division – Stacia Corp
# MENTOR    : Mr. Lakshman P V (Chief Operational Officer)
# DATE      : 29-05-2026
# VERSION   : v1.0
# ───────────────────────────────────────────────────
# DESCRIPTION:
# Historical logging viewer to search, filter, and review historical telemetry and manual inspections.
# ───────────────────────────────────────────────────
# DEPENDENCIES:
# streamlit, dashboards.utils.ui, dashboards.utils.db
# ───────────────────────────────────────────────────
# USAGE:
# Accessed via Streamlit sidebar navigation.
# ═══════════════════════════════════════════════════

import streamlit as st
from utils.ui import init_page, page_header
from utils.db import fetch_data

# =========================================
# PAGE CONFIG & AUTH (Must be first)
# =========================================
init_page("SentinelPulse AI - Telemetry History", required_role=["ADMIN", "TECHNICIAN"])

# =========================================
# PAGE HEADER
# =========================================
page_header("Telemetry History Log", "Search and filter past HVAC sensor recordings and AI model predictions.")

# =========================================
# FETCH FILTER DATA
# =========================================
try:
    machines_query = """
    SELECT DISTINCT machine_id FROM (
        SELECT machine_id FROM telemetry_data
        UNION
        SELECT machine_id FROM manual_inspections
    ) AS combined_machines ORDER BY machine_id
    """
    machines_df = fetch_data(machines_query)
    machine_list = ["All"] + machines_df["machine_id"].tolist()
except Exception as e:
    st.error(f"Error connecting to database: {e}")
    st.stop()

# =========================================
# FILTER UI
# =========================================
c1, c2, c3 = st.columns(3)
with c1:
    selected_machine = st.selectbox("Filter by Machine Asset", machine_list)
with c2:
    selected_risk = st.selectbox("Filter by Risk Level", ["All", "LOW", "MEDIUM", "HIGH", "CRITICAL"])
with c3:
    record_limit = st.selectbox("Limit Records", [100, 250, 500, 1000])

# =========================================
# TABS & DISPLAY LOGS
# =========================================
tab_telemetry, tab_inspections = st.tabs(["📊 Telemetry History", "📝 Manual Inspections"])

with tab_telemetry:
    # Telemetry Query
    query = "SELECT timestamp, machine_id, temperature, vibration, pressure, rpm, power_usage, health_score, failure_probability, anomaly_status, risk_level FROM telemetry_data WHERE 1=1"
    params = []

    if selected_machine != "All":
        query += " AND machine_id = %s"
        params.append(selected_machine)

    if selected_risk != "All":
        query += " AND risk_level = %s"
        params.append(selected_risk)

    query += " ORDER BY timestamp DESC LIMIT %s"
    params.append(record_limit)

    # Fetch filtered dataframe
    df = fetch_data(query, tuple(params))

    if not df.empty:
        st.markdown(f"**Displaying {len(df)} telemetry logs matching filters.**")
        st.dataframe(df, width='stretch', hide_index=True)
    else:
        st.info("No matching telemetry data found in the history database.")

with tab_inspections:
    # Manual Inspections Query
    ins_query = """
    SELECT inspection_time AS timestamp, technician_name, machine_id, 
           temperature, vibration, pressure, noise_level, 
           CASE WHEN oil_leakage = 1 THEN 'Yes' ELSE 'No' END AS oil_leakage,
           CASE WHEN overheating = 1 THEN 'Yes' ELSE 'No' END AS overheating,
           CASE WHEN abnormal_smell = 1 THEN 'Yes' ELSE 'No' END AS abnormal_smell,
           health_score, failure_probability, risk_level, remarks 
    FROM manual_inspections WHERE 1=1
    """
    ins_params = []

    if selected_machine != "All":
        ins_query += " AND machine_id = %s"
        ins_params.append(selected_machine)

    if selected_risk != "All":
        ins_query += " AND risk_level = %s"
        ins_params.append(selected_risk)

    ins_query += " ORDER BY inspection_time DESC LIMIT %s"
    ins_params.append(record_limit)

    # Fetch filtered dataframe
    df_ins = fetch_data(ins_query, tuple(ins_params))

    if not df_ins.empty:
        st.markdown(f"**Displaying {len(df_ins)} manual inspection logs matching filters.**")
        st.dataframe(df_ins, width='stretch', hide_index=True)
    else:
        st.info("No matching manual inspection records found in the database.")
