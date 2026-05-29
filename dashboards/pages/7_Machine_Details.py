import streamlit as st
import pandas as pd
import plotly.express as px
from utils.ui import init_page, page_header
from utils.db import fetch_data

# =========================================
# PAGE CONFIG & AUTH (Must be first)
# =========================================
init_page("SentinelPulse AI - Machine Intelligence", required_role=["ADMIN", "TECHNICIAN"])

# =========================================
# FETCH MACHINE LIST
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
    machine_list = machines_df["machine_id"].tolist()
except Exception as e:
    st.error(f"Error fetching machine metadata: {e}")
    st.stop()

# =========================================
# PAGE HEADER
# =========================================
page_header("Machine Intelligence Center", "Deep operational analytics for industrial assets")

if not machine_list:
    st.info("No machines registered in the telemetry database.")
    st.stop()

# =========================================
# MACHINE SELECTOR
# =========================================
selected_machine = st.selectbox("Select Asset to Analyze", machine_list)

# =========================================
# FETCH SELECTED MACHINE TELEMETRY
# =========================================
df = fetch_data(
    "SELECT * FROM telemetry_data WHERE machine_id = %s ORDER BY timestamp DESC LIMIT 500",
    (selected_machine,)
)

is_telemetry = True

# Fallback to manual inspections if telemetry data is empty
if df.empty:
    df = fetch_data(
        """
        SELECT inspection_time AS timestamp, machine_id, temperature, vibration, pressure,
               health_score, failure_probability, risk_level, remarks AS anomaly_status 
        FROM manual_inspections 
        WHERE machine_id = %s 
        ORDER BY inspection_time DESC LIMIT 500
        """,
        (selected_machine,)
    )
    is_telemetry = False

if df.empty:
    st.warning("No telemetry or manual inspection records found for the selected machine.")
    st.stop()

# Display source context notice
if not is_telemetry:
    st.info(f"Displaying details derived from Manual Inspection logs (No automated sensor telemetry available for {selected_machine}).")

latest = df.iloc[0]

# =========================================
# KPI METRICS
# =========================================
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.metric("Health Score", f"{latest['health_score']:.1f}")
with c2:
    st.metric("Failure Risk Probability", f"{latest['failure_probability']:.1f}%")
with c3:
    st.metric("Core Temperature", f"{latest['temperature']:.1f} °C")
with c4:
    st.metric("Vibration RMS", f"{latest['vibration']:.2f}")

st.markdown("---")

# =========================================
# LIVE STATUS BADGE
# =========================================
risk = latest["risk_level"]
if risk == "CRITICAL":
    st.error(f"ALERT: {selected_machine} is reporting CRITICAL risk parameters.")
elif risk == "HIGH":
    st.warning(f"WARNING: {selected_machine} is operating under HIGH risk parameters.")
else:
    st.success(f"NORMAL: {selected_machine} is operating stably.")

# =========================================
# PLOTLY CHART HELPER
# =========================================
def render_metric_chart(data, y_col, title, color):
    fig = px.line(
        data.sort_values("timestamp"),
        x="timestamp",
        y=y_col,
        title=title
    )
    fig.update_traces(line_color=color, line_width=2.5)
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
# GRAPH VISUALIZATIONS
# =========================================
st.subheader("Operational Trends" if is_telemetry else "Manual Inspection Trends")

tab1, tab2, tab3 = st.tabs(["Temperature", "Vibration", "Failure Probability"])

with tab1:
    render_metric_chart(df, "temperature", "Compressor Temperature (°C)", "#A855F7")
with tab2:
    render_metric_chart(df, "vibration", "Chassis Vibration Level (RMS)", "#6366F1")
with tab3:
    render_metric_chart(df, "failure_probability", "AI Failure Probability Trend (%)", "#F43F5E")

st.markdown("---")

# =========================================
# ANOMALY LOGS
# =========================================
if is_telemetry:
    st.subheader("Detected Anomalies History")
    anomaly_df = df[df["anomaly_status"] == "ANOMALY DETECTED"]
    if not anomaly_df.empty:
        st.dataframe(
            anomaly_df[["timestamp", "temperature", "vibration", "failure_probability", "risk_level"]],
            width='stretch',
            hide_index=True
        )
    else:
        st.success("No anomalies detected on this asset in the last 500 recordings.")
else:
    st.subheader("Manual Inspection Remarks History")
    if not df.empty:
        st.dataframe(
            df[["timestamp", "temperature", "vibration", "risk_level", "anomaly_status"]].rename(columns={"anomaly_status": "Remarks"}),
            width='stretch',
            hide_index=True
        )
    else:
        st.success("No manual inspections recorded.")

st.markdown("---")

# =========================================
# AI TROUBLESHOOTING INSIGHTS
# =========================================
st.subheader("Asset AI Recommendations")

insight_triggered = False

if latest["temperature"] > 80:
    st.warning("**High Core Temperature**: The compressor casing temperature is elevated. Inspect coil fins and airflow paths.")
    insight_triggered = True

if latest["vibration"] > 1.2:
    st.warning("**Vibration Instability**: The vibration RMS is high. Inspect rotor couplings and chassis mounting dampers.")
    insight_triggered = True

if latest["failure_probability"] > 80:
    st.error("**Urgent Action Required**: The asset failure probability is above critical threshold. Dispatch technician for immediate inspection.")
    insight_triggered = True

if not insight_triggered:
    st.success("**Stables Asset State**: All telemetry values conform to nominal operational ranges.")