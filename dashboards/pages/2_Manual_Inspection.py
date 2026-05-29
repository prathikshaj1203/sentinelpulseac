import streamlit as st
import pandas as pd
import numpy as np
import joblib
import os
from utils.ui import init_page, page_header
from utils.db import execute_query

# =========================================
# PAGE CONFIG & AUTH (Must be first)
# =========================================
init_page("SentinelPulse AI - Manual Inspection", required_role=["ADMIN", "TECHNICIAN"])

# =========================================
# PATH CONFIG & LOAD MODELS (Cached for performance)
# =========================================
@st.cache_resource
def load_ml_models():
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    model_path = os.path.join(base_dir, "ai_models", "compressor_model.pkl")
    scaler_path = os.path.join(base_dir, "ai_models", "scaler.pkl")
    encoder_path = os.path.join(base_dir, "ai_models", "encoder.pkl")
    return joblib.load(model_path), joblib.load(scaler_path), joblib.load(encoder_path)

try:
    model, scaler, encoder = load_ml_models()
except Exception as e:
    st.error(f"Error loading AI models: {e}")
    st.stop()

# =========================================
# PAGE HEADER
# =========================================
page_header("Manual HVAC Inspection", "Technician-based predictive maintenance analysis")

# =========================================
# MACHINE DETAILS
# =========================================
col1, col2 = st.columns(2)
with col1:
    ac_type = st.selectbox("AC Subsystem Type", ["Normal_AC", "Cassette_AC", "Centralized_AC"])
with col2:
    machine_id = st.text_input("HVAC Machine ID", "AC_101")

# =========================================
# INSPECTION FORM
# =========================================
st.subheader("Inspection Parameters")

with st.form("inspection_form"):
    c1, c2, c3 = st.columns(3)
    with c1:
        overheating = st.selectbox("Overheating State", ["No", "Mild", "Severe"])
        strange_noise = st.selectbox("Acoustic Noise level", ["Low", "Medium", "High"])
        airflow_issue = st.selectbox("Airflow Obstruction", ["No", "Yes"])
    with c2:
        oil_leakage = st.selectbox("Oil/Coolant Leakage", ["No", "Yes"])
        vibration_level = st.selectbox("Physical Vibration Level", ["Low", "Medium", "High"])
        cooling_efficiency = st.selectbox("Cooling Efficiency", ["Good", "Average", "Poor"])
    with c3:
        pressure_issue = st.selectbox("Pressure Stability", ["Stable", "Moderate", "Unstable"])
        humidity_issue = st.selectbox("High Humidity Level", ["No", "Yes"])
        power_issue = st.selectbox("Power Load Draw", ["Normal", "High"])

    st.markdown("<br>", unsafe_allow_html=True)
    predict_button = st.form_submit_button("Run AI Diagnosis", width='stretch')

# =========================================
# DIAGNOSIS PROCESSING
# =========================================
if predict_button:
    # Feature mappings
    temperature = {"No": 50, "Mild": 72, "Severe": 95}[overheating]
    vibration = {"Low": 0.3, "Medium": 1.0, "High": 1.8}[vibration_level]
    noise_db = {"Low": 40, "Medium": 65, "High": 90}[strange_noise]
    pressure = {"Stable": 1.0, "Moderate": 2.0, "Unstable": 3.5}[pressure_issue]
    humidity = 75 if humidity_issue == "Yes" else 45
    hvac_power = 95 if power_issue == "High" else 45
    airflow = 150 if airflow_issue == "Yes" else 320
    cooling = {"Good": 90, "Average": 65, "Poor": 30}[cooling_efficiency]
    oil_temp = 88 if oil_leakage == "Yes" else 50

    # Build input features
    features = pd.DataFrame([{
        "rpm": 500,
        "motor_power": hvac_power,
        "torque": 45,
        "outlet_pressure_bar": pressure,
        "air_flow": airflow,
        "noise_db": noise_db,
        "outlet_temp": temperature,
        "oil_tank_temp": oil_temp,
        "vibration": vibration,
        "tp2_pressure": pressure,
        "tp3_pressure": pressure + 1,
        "metro_oil_temp": oil_temp,
        "motor_current": 1.2,
        "dv_pressure": pressure,
        "supply_temp": 22,
        "return_temp": 28,
        "humidity": humidity,
        "hvac_power": hvac_power,
        "energy": cooling,
        "ac_type": encoder.transform([ac_type])[0]
    }])

    # Model Inference
    scaled_features = scaler.transform(features)
    prediction = model.predict(scaled_features)[0]
    probability_percent = model.predict_proba(scaled_features)[0][1] * 100
    health_score = 100 - probability_percent

    # Risk level thresholding
    if probability_percent > 80:
        risk = "CRITICAL"
    elif probability_percent > 60:
        risk = "HIGH"
    elif probability_percent > 35:
        risk = "MEDIUM"
    else:
        risk = "LOW"

    # Analyze anomalies for remarks
    diagnosis = []
    if vibration > 1.5:
        diagnosis.append("Possible bearing wear detected")
    if pressure > 3:
        diagnosis.append("Pressure instability observed")
    if temperature > 85:
        diagnosis.append("Severe overheating detected")
    if airflow < 200:
        diagnosis.append("Restricted airflow suspected")
    
    remarks = " | ".join(diagnosis) if diagnosis else "No major abnormalities detected"

    # =====================================
    # SAVE INSPECTION TO DATABASE
    # =====================================
    try:
        insert_query = """
        INSERT INTO manual_inspections (
            technician_name, machine_id, temperature, vibration, pressure, noise_level,
            oil_leakage, overheating, abnormal_smell, health_score, failure_probability,
            predicted_failure, risk_level, remarks
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        execute_query(insert_query, (
            st.session_state.get("full_name", "Technician"),
            machine_id,
            float(temperature),
            float(vibration),
            float(pressure),
            float(noise_db),
            1 if oil_leakage == "Yes" else 0,
            1 if overheating != "No" else 0,
            1 if strange_noise != "Low" else 0,
            float(health_score),
            float(probability_percent),
            int(prediction),
            risk,
            remarks
        ))
        st.success("Diagnostic report saved to system history database.")
    except Exception as e:
        st.error(f"Failed to save inspection report: {e}")

    # =====================================
    # RESULTS UI
    # =====================================
    st.markdown("---")
    st.subheader("AI Diagnostic Report")

    r1, r2, r3 = st.columns(3)
    with r1:
        st.metric("Failure Probability", f"{probability_percent:.1f}%")
    with r2:
        st.metric("Health Score", f"{health_score:.1f}")
    with r3:
        st.metric("Assessed Risk Level", risk)

    st.markdown("### AI Findings")
    if diagnosis:
        for item in diagnosis:
            st.warning(f"{item}")
    else:
        st.success("No physical or mechanical anomalies identified.")

    st.markdown("### Maintenance Recommendation")
    if risk == "CRITICAL":
        st.error("EMERGENCY: Schedule immediate shutdown and manual inspection.")
    elif risk == "HIGH":
        st.warning("URGENT: Schedule maintenance check within 24 hours.")
    else:
        st.success("NORMAL: Keep normal operation. Routine maintenance schedule stands.")