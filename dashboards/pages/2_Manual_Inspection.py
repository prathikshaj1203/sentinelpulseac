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

    # Analyze anomalies for detailed remarks and findings
    diagnosis_summary = []
    detailed_findings = []
    
    if vibration > 1.5:
        diagnosis_summary.append("Possible bearing wear")
        detailed_findings.append(
            f"⚠️ **Physical Vibration Level ({vibration:.2f} mm/s - High)**: "
            "High vibration levels indicate mechanical imbalance, shaft misalignment, or bearing sleeve wear. "
            "Prolonged operation under these conditions will cause permanent damage to rotor components."
        )
    if pressure > 3.0:
        diagnosis_summary.append("Pressure instability")
        detailed_findings.append(
            f"⚠️ **Pressure Stability ({pressure:.1f} bar - Unstable)**: "
            "Extreme discharge or suction pressure deviation detected. This suggests potential expansion valve blockage, "
            "compressor valve leakage, or refrigerant loop restriction."
        )
    if temperature > 85:
        diagnosis_summary.append("Severe overheating")
        detailed_findings.append(
            f"⚠️ **Severe Overheating ({temperature:.1f} °C - Severe)**: "
            "Discharge air temperature is dangerously elevated. This places the motor windings at critical risk of "
            "thermal breakdown and permanent compressor failure."
        )
    if airflow < 200:
        diagnosis_summary.append("Restricted airflow")
        detailed_findings.append(
            f"⚠️ **Airflow Obstruction ({airflow} CFM - Restricted)**: "
            "Airflow has dropped below standard operating thresholds. This typically indicates a clogged air filter, "
            "damper failure, or evaporator coil icing."
        )
    if noise_db > 75:
        diagnosis_summary.append("High acoustic noise")
        detailed_findings.append(
            f"⚠️ **Acoustic Noise level ({noise_db} dB - High)**: "
            "Operating noise is significantly elevated, indicating potential housing loose bolts, mechanical grinding, "
            "or fan blade deflection."
        )
    if oil_leakage == "Yes":
        diagnosis_summary.append("Active leakage")
        detailed_findings.append(
            "⚠️ **Coolant/Oil Leakage (Confirmed)**: "
            "Visual fluid leakage observed. Fluid loss degrades motor lubrication, increases internal friction, "
            "and will eventually cause lockup or refrigerant venting."
        )
    if cooling_efficiency == "Poor":
        diagnosis_summary.append("Poor cooling efficiency")
        detailed_findings.append(
            "⚠️ **Cooling Output (Degraded)**: "
            "Thermodynamic performance is highly degraded. The system is consuming nominal power but fails to lower "
            "temperatures to spec. Inspect the condenser coils and return loop."
        )
    if humidity_issue == "Yes":
        diagnosis_summary.append("Elevated humidity")
        detailed_findings.append(
            f"⚠️ **High Humidity Level ({humidity}% - Elevated)**: "
            "Elevated moisture levels are taxing the cooling capacity, leading to condensation build-up and "
            "increased risk of corrosion or mold growth."
        )
    if power_issue == "High":
        diagnosis_summary.append("High power draw")
        detailed_findings.append(
            f"⚠️ **Power Load Draw ({hvac_power} kW - Excessive)**: "
            "The electrical current drawn is above nominal rating. This indicates high motor load due to mechanical friction, "
            "or failing electrical contacts/capacitor."
        )

    remarks = " | ".join(diagnosis_summary) if diagnosis_summary else "No major abnormalities detected"

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
    if detailed_findings:
        for item in detailed_findings:
            st.warning(item)
    else:
        st.success("No physical or mechanical anomalies identified. All subsystems are operating within standard tolerance bands.")

    st.markdown("### Maintenance Recommendation Report")
    
    # Render short warning/status banner
    if risk == "CRITICAL":
        st.error("🚨 **EMERGENCY STATUS**: Immediate system shutdown and manual inspection recommended.")
    elif risk == "HIGH":
        st.warning("⚠️ **URGENT STATUS**: Schedule technical maintenance check within 24 hours.")
    elif risk == "MEDIUM":
        st.info("ℹ️ **PRECAUTIONARY STATUS**: Schedule inspection during next routine maintenance cycle.")
    else:
        st.success("✅ **NOMINAL STATUS**: Keep normal operation. Standard schedule stands.")

    # Dropdown selector for the detailed report sections
    selected_section = st.selectbox(
        "Choose Detailed Maintenance Report Section to view/print:",
        ["Executive Summary & Immediate Actions", "Technical Troubleshooting Guide", "Required Tools & Safety Checklist", "Future Preventive Maintenance Schedule"]
    )

    if risk == "CRITICAL":
        if selected_section == "Executive Summary & Immediate Actions":
            st.markdown("""
            ### 📝 Executive Summary
            * **Status**: Critical mechanical/electrical deviation.
            * **Urgency**: Immediate (Within 1 hour).
            * **Summary**: Multiple operational parameters (such as extreme temperature or excessive physical vibration) have crossed safety thresholds, indicating active component failure. Continued operation risks complete compressor destruction or electrical fire.
            * **Action**: Order immediate system lockout and isolate the power supply.
            """)
        elif selected_section == "Technical Troubleshooting Guide":
            st.markdown("""
            ### 🛠️ Step-by-Step Technical Guide
            1. **Isolate Power**: De-energize the unit at the local disconnect box. Apply Lock-Out Tag-Out (LOTO).
            2. **Pressure Equalization**: Attach manifold gauge set and check high/low pressure differentials.
            3. **Inspect Bearings**: Measure shaft axial play and check for metallic shavings in the oil pan.
            4. **Clean Fins**: Visually inspect the condenser coils and clean off debris or scale deposits.
            5. **Re-Test**: Power on briefly under controlled current monitoring to confirm current draw settles.
            """)
        elif selected_section == "Required Tools & Safety Checklist":
            st.markdown("""
            ### 🧰 Safety & Tooling Checklist
            * **Tools Needed**: Laser Shaft Alignment kit, digital refrigerant manifold gauges, clamp-on multimeter, torque wrench.
            * **PPE Required**: Electrical insulated gloves (Class 00), protective face shield, steel-toe safety boots.
            * **Safety Rules**: Ensure 2-person buddy system is active for high-voltage panel checks.
            """)
        elif selected_section == "Future Preventive Maintenance Schedule":
            st.markdown("""
            ### 📅 Future Preventive Actions
            * **Short-Term**: Increase telemetry monitoring frequency to 5-minute intervals for the next 7 days.
            * **Mid-Term**: Schedule full compressor oil analysis and change liquid line filter drier within 15 days.
            * **Long-Term**: Replace baseline vibration dampers on the mounting base.
            """)

    elif risk == "HIGH":
        if selected_section == "Executive Summary & Immediate Actions":
            st.markdown("""
            ### 📝 Executive Summary
            * **Status**: Significant parameter degradation detected.
            * **Urgency**: Urgent (Within 24 hours).
            * **Summary**: The system has shown signs of performance loss and moderate thermal/vibration stress. Scheduled technician checks are needed immediately to prevent escalation.
            * **Action**: Assign a technician work order for detailed inspection.
            """)
        elif selected_section == "Technical Troubleshooting Guide":
            st.markdown("""
            ### 🛠️ Step-by-Step Technical Guide
            1. **Filter Review**: Check primary and secondary air filters; replace if pressure drop exceeds 150 Pa.
            2. **Leak Detection**: Use electronic leak detector or bubble test along all joint seals.
            3. **Inspect Belt/Coupling**: Inspect motor-blower drive belt tension and adjust as needed.
            4. **Coil Inspection**: Spray foam cleaner on the outdoor condenser fins and wash down.
            """)
        elif selected_section == "Required Tools & Safety Checklist":
            st.markdown("""
            ### 🧰 Safety & Tooling Checklist
            * **Tools Needed**: Electronic leak detector, fin comb tool, replacement MERV 13 filters, chemical foam spray.
            * **PPE Required**: Safety glasses, nitrile chemical-resistant gloves, dust respirator mask.
            """)
        elif selected_section == "Future Preventive Maintenance Schedule":
            st.markdown("""
            ### 📅 Future Preventive Actions
            * **Short-Term**: Re-check system parameters via the dashboard after 24 hours of operation.
            * **Mid-Term**: Schedule comprehensive diagnostic test in the next monthly service.
            """)

    elif risk == "MEDIUM":
        if selected_section == "Executive Summary & Immediate Actions":
            st.markdown("""
            ### 📝 Executive Summary
            * **Status**: Mild parameter deviation from base.
            * **Urgency**: Routine (Within 7 days).
            * **Summary**: Low-level anomalies detected. Performance is currently acceptable, but preventive maintenance will prevent long-term component wear.
            * **Action**: Include in the weekly maintenance run.
            """)
        elif selected_section == "Technical Troubleshooting Guide":
            st.markdown("""
            ### 🛠️ Step-by-Step Technical Guide
            1. **General Cleaning**: Clear debris from the outdoor condenser unit's vicinity.
            2. **Tighten Fasteners**: Inspect electrical terminal connections and tighten loose screws.
            3. **Check Damper**: Manually cycle dampers to confirm full range of motion.
            """)
        elif selected_section == "Required Tools & Safety Checklist":
            st.markdown("""
            ### 🧰 Safety & Tooling Checklist
            * **Tools Needed**: Screwdriver set, contact cleaner spray, basic hand tools.
            * **PPE Required**: Safety glasses, standard work gloves.
            """)
        elif selected_section == "Future Preventive Maintenance Schedule":
            st.markdown("""
            ### 📅 Future Preventive Actions
            * **Short-Term**: Monitor telemetry on the sensor tracking page.
            * **Mid-Term**: Perform standard quarterly checkups.
            """)

    else:
        if selected_section == "Executive Summary & Immediate Actions":
            st.markdown("""
            ### 📝 Executive Summary
            * **Status**: Subsystems healthy.
            * **Urgency**: Nominal.
            * **Summary**: All components are running cleanly and inside designed efficiency ranges. No corrective actions are required at this time.
            * **Action**: Maintain standard operating procedures.
            """)
        elif selected_section == "Technical Troubleshooting Guide":
            st.markdown("""
            ### 🛠️ Step-by-Step Technical Guide
            * No active faults to troubleshoot. 
            * Run a manual diagnostic self-test to verify sensor calibration.
            """)
        elif selected_section == "Required Tools & Safety Checklist":
            st.markdown("""
            ### 🧰 Safety & Tooling Checklist
            * **Tools Needed**: None.
            * **PPE Required**: Standard safety boots.
            """)
        elif selected_section == "Future Preventive Maintenance Schedule":
            st.markdown("""
            ### 📅 Future Preventive Actions
            * **Next Inspection**: Schedule standard monthly preventive maintenance in 30 days.
            """)