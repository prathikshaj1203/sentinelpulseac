import streamlit as st
from utils.ui import init_page, page_header
from utils.db import fetch_data, execute_query

# =========================================
# PAGE CONFIG & AUTH (Must be first)
# =========================================
init_page("SentinelPulse AI - Alert Center", required_role=["ADMIN", "TECHNICIAN"])

# =========================================
# FETCH ALERTS
# =========================================
try:
    df = fetch_data("SELECT * FROM alerts ORDER BY timestamp DESC")
except Exception as e:
    st.error(f"Error fetching alerts: {e}")
    st.stop()

# =========================================
# PAGE HEADER
# =========================================
page_header("Industrial Alert Center", "AI-generated maintenance alerts")

# Inject styling to reduce button size
st.markdown("""
<style>
div[data-testid="stButton"] button {
    padding-top: 2px !important;
    padding-bottom: 2px !important;
    font-size: 13px !important;
    height: 32px !important;
}
</style>
""", unsafe_allow_html=True)

# =========================================
# ACTIVE ALERTS SECTION
# =========================================
active_alerts = df[~df["acknowledged"]]

st.subheader("Active Maintenance Alerts")

if not active_alerts.empty:
    col_btn1, col_btn2 = st.columns([0.25, 0.75])
    with col_btn1:
        if st.button("Acknowledge All", key="ack_all", use_container_width=True):
            execute_query("UPDATE alerts SET acknowledged = TRUE WHERE acknowledged = FALSE")
            st.success("All active alerts acknowledged.")
            st.rerun()

    st.markdown("###")
    selected_alert_ids = []

    # Display alerts list with selection checkboxes
    for _, row in active_alerts.iterrows():
        col_check, col_content = st.columns([0.05, 0.95])
        with col_check:
            st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)
            is_selected = st.checkbox("", key=f"select_{row['id']}")
            if is_selected:
                selected_alert_ids.append(row['id'])
                
        with col_content:
            severity = row["severity"]
            alert_msg = f"**{row['machine_id']}** — {row['message']}  \n*Timestamp: {row['timestamp']}*"
            
            if severity == "CRITICAL":
                st.error(alert_msg)
            else:
                st.warning(alert_msg)

    # Acknowledge selected alerts button
    if selected_alert_ids:
        st.markdown("###")
        if st.button(f"Acknowledge Selected ({len(selected_alert_ids)})", key="ack_selected"):
            if len(selected_alert_ids) == 1:
                execute_query("UPDATE alerts SET acknowledged = TRUE WHERE id = %s", (selected_alert_ids[0],))
            else:
                placeholders = ", ".join(["%s"] * len(selected_alert_ids))
                execute_query(f"UPDATE alerts SET acknowledged = TRUE WHERE id IN ({placeholders})", tuple(selected_alert_ids))
            st.success(f"Successfully acknowledged {len(selected_alert_ids)} alerts.")
            st.rerun()
else:
    st.success("No active alerts. All machines operating within normal thresholds.")

st.markdown("---")

# =========================================
# HISTORICAL ALERTS ARCHIVE
# =========================================
st.subheader("Alert Archive Logs")
st.dataframe(df, width='stretch', hide_index=True)