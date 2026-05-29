import streamlit as st
import pandas as pd
from streamlit_autorefresh import st_autorefresh
from datetime import datetime
from utils.ui import init_page, page_header
from utils.db import fetch_data

# =========================================
# PAGE CONFIG & AUTH (Must be first)
# =========================================
init_page("SentinelPulse AI - Home", required_role="ADMIN")

# Live connection header status
st.success("LIVE SYSTEM ACTIVE | Kafka Streaming Operational | AI Engine Running")

# =========================================
# AUTO REFRESH
# =========================================
st_autorefresh(interval=5000, key="dashboard_refresh")

st.caption(f"Last Synchronized: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# =========================================
# FETCH TELEMETRY DATA
# =========================================
df = fetch_data("SELECT * FROM telemetry_data ORDER BY timestamp DESC LIMIT 500")

# =========================================
# PAGE HEADER
# =========================================
page_header("SentinelPulse AI", "Industrial HVAC Predictive Maintenance Platform")
if df.empty:
    st.info("Waiting for live telemetry stream data...")
    st.stop()

# =========================================
# KPI METRICS
# =========================================
total_machines = df["machine_id"].nunique()
critical_count = len(df[df["risk_level"] == "CRITICAL"])
avg_health = df["health_score"].mean()
avg_failure = df["failure_probability"].mean()

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.metric("Active Machines", total_machines)
with c2:
    st.metric("Critical Machines", critical_count)
with c3:
    st.metric("Average Health", f"{avg_health:.2f}")
with c4:
    st.metric("Avg Failure Risk", f"{avg_failure:.2f}%")

st.markdown("---")

# =========================================
# LIVE ALERT CENTER
# =========================================
st.subheader("Live Alert Center")

critical_df = df[df["risk_level"] == "CRITICAL"]

if len(critical_df) > 0:
    for _, row in critical_df.head(5).iterrows():
        st.markdown(f"""
<div style="background: rgba(239, 68, 68, 0.05); border: 1px solid rgba(239, 68, 68, 0.25); border-left: 5px solid #EF4444; border-radius: 12px; padding: 16px 20px; margin-bottom: 12px; box-shadow: 0 0 15px rgba(239, 68, 68, 0.15);">
<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
<span style="font-weight: 700; color: #EF4444; font-size: 14px; letter-spacing: 0.5px;">CRITICAL RISK DETECTED — {row['machine_id']}</span>
<span style="font-size: 12px; color: #9CA3AF;">{row['timestamp']}</span>
</div>
<div style="display: flex; gap: 30px; font-size: 13px; color: #E5E7EB;">
<div>Prob. Failure: <b style="color: #EF4444;">{row['failure_probability']:.1f}%</b></div>
<div>Temp: <b>{row['temperature']:.1f}°C</b></div>
<div>Vibration: <b>{row['vibration']:.2f}</b></div>
</div>
</div>
""", unsafe_allow_html=True)
else:
    st.markdown("""
<div style="background: rgba(16, 185, 129, 0.05); border: 1px solid rgba(16, 185, 129, 0.25); border-left: 5px solid #10B981; border-radius: 12px; padding: 16px 20px; box-shadow: 0 0 10px rgba(16, 185, 129, 0.05);">
<span style="font-weight: 600; color: #10B981; font-size: 14px;">ALL SYSTEMS OPERATIONAL — No active critical risk alerts detected.</span>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# =========================================
# DIGITAL TWIN GRID
# =========================================
st.subheader("Digital Twin Machine Grid")

latest_machines = df.drop_duplicates(subset="machine_id")
grid_cols = st.columns(3)

for index, (_, row) in enumerate(latest_machines.iterrows()):
    with grid_cols[index % 3]:
        risk = row["risk_level"]
        anomaly = row["anomaly_status"]

        # Dynamic neon color styling matching risk
        if risk == "CRITICAL":
            color, shadow = "#EF4444", "rgba(239, 68, 68, 0.25)"
        elif risk == "HIGH":
            color, shadow = "#F97316", "rgba(249, 115, 22, 0.2)"
        elif risk == "MEDIUM":
            color, shadow = "#FBBF24", "rgba(251, 191, 36, 0.15)"
        else:
            color, shadow = "#10B981", "rgba(16, 185, 129, 0.15)"

        anomaly_badge = f"""<span style="background:{'rgba(239,68,68,0.2)' if anomaly == 'ANOMALY DETECTED' else 'rgba(16,185,129,0.2)'};color:{'#FCA5A5' if anomaly == 'ANOMALY DETECTED' else '#A7F3D0'};padding:3px 10px; border-radius:8px; font-size:11px; font-weight:700; border: 1px solid {'rgba(239,68,68,0.4)' if anomaly == 'ANOMALY DETECTED' else 'rgba(16,185,129,0.4)'};">{anomaly}</span>"""

        st.markdown(f"""
<div style="background: rgba(15, 15, 28, 0.6); padding: 22px; border-radius: 18px; border: 1px solid {color}40; box-shadow: 0 4px 20px rgba(0,0,0,0.3), 0 0 15px {shadow}; margin-bottom: 20px; backdrop-filter: blur(10px);">
<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
<h3 style="margin: 0; font-size: 20px; font-weight: 700; color: #FFF;">{row['machine_id']}</h3>
{anomaly_badge}
</div>
<div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; font-size: 13px; border-top: 1px solid rgba(168, 85, 247, 0.15); padding-top: 12px; margin-bottom: 12px;">
<div>Health Score: <b style="color:#C084FC;">{row['health_score']:.1f}</b></div>
<div>Risk Prob: <b style="color:{color};">{row['failure_probability']:.1f}%</b></div>
<div>Risk Level: <span style="text-transform: uppercase; font-weight:700; color:{color};">{row['risk_level']}</span></div>
</div>
<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px; font-size: 12px; border-top: 1px dashed rgba(255,255,255,0.08); padding-top: 10px; color: #9CA3AF;">
<div>Temp: <b style="color:#FFF;">{row['temperature']:.1f} °C</b></div>
<div>Vib: <b style="color:#FFF;">{row['vibration']:.2f}</b></div>
<div>RPM: <b style="color:#FFF;">{row['rpm']}</b></div>
<div>Power: <b style="color:#FFF;">{row['power_usage']:.1f} kW</b></div>
</div>
</div>
""", unsafe_allow_html=True)

# =========================================
# MACHINE HEALTH RANKING
# =========================================
st.subheader("Machine Health Ranking")

ranking_df = df.groupby("machine_id")["health_score"].mean().reset_index()
ranking_df = ranking_df.sort_values(by="health_score", ascending=False)
ranking_df.columns = ["Machine ID", "Mean Health Score"]

st.dataframe(ranking_df, width='stretch', hide_index=True)

st.markdown("---")

# =========================================
# AI SYSTEM INSIGHTS
# =========================================
st.subheader("AI Insights & Pipelines")

highest_risk = df.sort_values(by="failure_probability", ascending=False).iloc[0]

st.warning(f"""
**Highest Risk Asset Alert**: **{highest_risk['machine_id']}** is showing the highest failure probability in the network at **{highest_risk['failure_probability']:.1f}%**. Immediate manual maintenance inspection is recommended.
""")

col_pipeline1, col_pipeline2, col_pipeline3 = st.columns(3)
with col_pipeline1:
    st.info("**Kafka Stream Pipeline**: Active & Streaming Live telemetry telemetry_data.")
with col_pipeline2:
    st.info("**AI Model Predictor**: Active with live Scikit-learn anomaly analysis.")
with col_pipeline3:
    st.info("**Grafana Observability**: Connected to Postgres telemetry dashboard.")