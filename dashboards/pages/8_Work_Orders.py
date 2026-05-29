import streamlit as st
import pandas as pd
from utils.ui import init_page, page_header
from utils.db import fetch_data, execute_query

# =========================================
# PAGE CONFIG & AUTH (Must be first)
# =========================================
init_page("SentinelPulse AI - Work Orders", required_role=["ADMIN", "TECHNICIAN"])

# =========================================
# FETCH WORK ORDERS & MACHINES
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
    
    # Load all work orders
    df = fetch_data("SELECT * FROM work_orders ORDER BY created_at DESC")
except Exception as e:
    st.error(f"Error loading maintenance workspace: {e}")
    st.stop()

# =========================================
# PAGE HEADER
# =========================================
page_header("Maintenance Work Orders", "Industrial maintenance workflow management")

# =========================================
# CREATE WORK ORDER FORM
# =========================================
st.subheader("Create Maintenance Work Order")

with st.form("work_order_form"):
    c1, c2 = st.columns(2)
    with c1:
        machine_id = st.selectbox("Select Asset", machine_list)
        issue_type = st.selectbox("Issue Type", ["Overheating", "Vibration", "Pressure Instability", "Compressor Failure", "Airflow Reduction"])
    with c2:
        severity = st.selectbox("Severity Level", ["LOW", "MEDIUM", "HIGH", "CRITICAL"])
        assigned_to = st.text_input("Assign Technician Name")
        
    description = st.text_area("Issue / Diagnosis Details")
    submitted = st.form_submit_button("Create Work Order", width='stretch')

    if submitted:
        if not assigned_to:
            st.error("Please assign a technician to the work order.")
        else:
            try:
                insert_query = """
                INSERT INTO work_orders (machine_id, issue_type, severity, assigned_to, status, description)
                VALUES (%s, %s, %s, %s, %s, %s)
                """
                execute_query(insert_query, (machine_id, issue_type, severity, assigned_to, "OPEN", description))
                st.success("Work order created and assigned successfully.")
                st.rerun()
            except Exception as e:
                st.error(f"Failed to create work order: {e}")

st.markdown("---")

# =========================================
# ACTIVE WORK ORDERS SECTION
# =========================================
st.subheader("Active Work Orders")

active_orders = df[df["status"] != "COMPLETED"] if not df.empty else pd.DataFrame()

if not active_orders.empty:
    for _, row in active_orders.iterrows():
        order_sev = row["severity"]
        card_content = f"""
        **Work Order #{row['id']}**  
        **Asset**: `{row['machine_id']}` | **Issue**: `{row['issue_type']}` | **Technician**: `{row['assigned_to']}`  
        **Details**: *{row['description']}*  
        *Created: {row['created_at']}*
        """
        
        col_content, col_action = st.columns([0.8, 0.2])
        
        with col_content:
            if order_sev == "CRITICAL":
                st.error(f"**CRITICAL RISK**  \n{card_content}")
            elif order_sev == "HIGH":
                st.warning(f"**HIGH RISK**  \n{card_content}")
            else:
                st.info(f"**NORMAL RISK**  \n{card_content}")
                
        with col_action:
            st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)
            if st.button(f"Mark Complete", key=f"complete_{row['id']}", width='stretch'):
                try:
                    execute_query(
                        "UPDATE work_orders SET status = 'COMPLETED', completed_at = CURRENT_TIMESTAMP WHERE id = %s",
                        (row["id"],)
                    )
                    st.success(f"Work order #{row['id']} marked complete.")
                    st.rerun()
                except Exception as e:
                    st.error(f"Failed to update status: {e}")
else:
    st.success("No active work orders. All scheduled maintenance items are complete.")

st.markdown("---")

# =========================================
# WORK ORDER HISTORY TABLE
# =========================================
st.subheader("Work Order Archives")
if not df.empty:
    st.dataframe(df, width='stretch', hide_index=True)
else:
    st.info("No work orders registered in the archives.")