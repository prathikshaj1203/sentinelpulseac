# ───────────────────────────────────────────────────
# PROJECT   : SentinelPulse AI – Real-Time Predictive Maintenance System for Industrial Air Compressors
# FILE      : 2_Manual_Inspection.py
# AUTHOR    : PRATHIKSHA J
# INTERN ID : SIT067
# DIVISION  : Software & AI Division – Stacia Corp
# MENTOR    : Mr. Lakshman P V (Chief Operational Officer)
# DATE      : 29-05-2026
# VERSION   : v1.0
# ───────────────────────────────────────────────────
# DESCRIPTION:
# Technician manual inspection logger utilizing predictive models to assess failure risks and generate action reports.
# ───────────────────────────────────────────────────
# DEPENDENCIES:
# streamlit, pandas, numpy, joblib, os, dashboards.utils.ui, dashboards.utils.db
# ───────────────────────────────────────────────────
# USAGE:
# Accessed via Streamlit sidebar navigation.
# ═══════════════════════════════════════════════════

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
            f"⚠️ **Physical Vibration Level ({vibration:.2f} mm/s - High Vibration Warning)**:\n"
            "The measured mechanical vibration exceeds the safe baseline threshold of 1.5 mm/s. "
            "This suggests dynamic imbalance, misalignment of the motor-compressor coupling shaft, or mechanical loosening of the chassis. "
            "Sustained high vibration forces lead to accelerated fatigue in bearing sleeves, stator coil insulation breakdown, "
            "and structural damage to mounting foundation anchors. Immediate laser alignment testing and mounting torque validation are required."
        )
    if pressure > 3.0:
        diagnosis_summary.append("Pressure instability")
        detailed_findings.append(
            f"⚠️ **Pressure Stability ({pressure:.1f} bar - Unstable Pressure Warning)**:\n"
            "The discharge/suction pressure ratio has deviated significantly from the stable operating range. "
            "This indicates refrigerant flow restriction, expansion valve orifice clogging, or internal compressor valve seat leakage. "
            "Operating with unstable pressure leads to short-cycling, high thermal stress on the motor windings, and oil migration from the sump. "
            "Verify superheat values and inspect the expansion valve for ice or debris accumulation."
        )
    if temperature > 85:
        diagnosis_summary.append("Severe overheating")
        detailed_findings.append(
            f"⚠️ **Severe Overheating ({temperature:.1f} °C - Critical Temperature Alert)**:\n"
            "The discharge port temperature is operating at a dangerous level. This is typically caused by condenser fan failure, "
            "scale build-up on heat exchanger surfaces, or refrigerant charge deficiency. "
            "Excessive discharge temperature degrades compressor oil viscosity, leading to metal-on-metal friction, bearing scoring, "
            "and terminal winding burnout. Complete electrical isolation is strongly recommended until thermal levels return to normal."
        )
    if airflow < 200:
        diagnosis_summary.append("Restricted airflow")
        detailed_findings.append(
            f"⚠️ **Airflow Obstruction ({airflow} CFM - Restricted Airflow Warning)**:\n"
            "The measured volumetric airflow is below the minimum required boundary of 200 CFM. "
            "This is caused by high dust load on the MERV intake filters, supply/return damper jamming, or ice formation on the evaporator coils. "
            "Low airflow prevents proper heat absorption, leading to liquid floodback to the compressor (which can break scroll/reciprocating components) "
            "and system efficiency loss. Immediate filter inspection and coil defrost cycle check are required."
        )
    if noise_db > 75:
        diagnosis_summary.append("High acoustic noise")
        detailed_findings.append(
            f"⚠️ **Acoustic Noise level ({noise_db} dB - High Acoustic Noise Warning)**:\n"
            "The acoustic signature has spiked to high decibel levels. This noise profile points to loose structural panels, "
            "blower fan wheel imbalance, or severe mechanical grinding inside the motor casing. "
            "If unaddressed, it can lead to mounting bracket failure, fan blade detachment, and permanent damage to auxiliary drive shafts."
        )
    if oil_leakage == "Yes":
        diagnosis_summary.append("Active leakage")
        detailed_findings.append(
            "⚠️ **Coolant/Oil Leakage (Confirmed Fluid Loss Alert)**:\n"
            "Active liquid or oil film detected on the refrigeration line joints or under the compressor crankcase. "
            "Oil leakage depletes the compressor oil sump, leading to insufficient lubrication, dry bearing friction, and total lockup. "
            "Furthermore, it suggests an active refrigerant leak, which will lead to low cooling capacity and environmental compliance violations. "
            "Isolate the system and perform a pressurized nitrogen leak test."
        )
    if cooling_efficiency == "Poor":
        diagnosis_summary.append("Poor cooling efficiency")
        detailed_findings.append(
            "⚠️ **Cooling Output (Degraded Thermodynamic Performance)**:\n"
            "The system cooling efficiency has degraded. The HVAC unit is drawing normal power but failing to maintain design space temperature. "
            "This mismatch is caused by low heat transfer efficiency, evaporator coil blockages, or refrigerant charge drift. "
            "Inspect the thermostatic expansion valve bulb and clean both evaporator and condenser coil surfaces."
        )
    if humidity_issue == "Yes":
        diagnosis_summary.append("Elevated humidity")
        detailed_findings.append(
            f"⚠️ **High Humidity Level ({humidity}% - High Latent Load Warning)**:\n"
            "The ambient humidity has risen, creating an elevated latent cooling load. This forces the system to run longer cycles "
            "to extract moisture, causing excessive water condensation in the drain pan. "
            "Ensure condensate drain lines are clear, inspect trap operation, and verify that the indoor fan speed is adjusted to nominal rate."
        )
    if power_issue == "High":
        diagnosis_summary.append("High power draw")
        detailed_findings.append(
            f"⚠️ **Power Load Draw ({hvac_power} kW - Excessive Electrical Draw)**:\n"
            "The electric power consumption has reached a critical peak. High power draw occurs when the compressor motor is working "
            "against severe mechanical friction (e.g. worn bearings, tight shafts) or when stator electrical winding insulation is degrading. "
            "It can also indicate low voltage supply or loose electrical terminals. Immediate circuit breaker load checks and contactor inspections are required."
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

    # Wrap the entire report in a single expander (dropdown report)
    with st.expander("📋 Click to Expand Full Detailed Maintenance Recommendation Report", expanded=False):
        if risk == "CRITICAL":
            st.markdown(f"""
            ## 🚨 EMERGENCY MAINTENANCE ACTION REPORT
            
            ### 📝 Executive Summary
            The HVAC system (ID: **{machine_id}**, Subsystem: **{ac_type}**) is currently operating under **CRITICAL mechanical and thermodynamic failure conditions**. Multiple monitored metrics, including severe vibration, extreme temperature, and degraded pressure stability, have breached their critical safety threshold limits. 
            
            This combination of faults indicates that a major failure of key compressor or motor components is actively occurring. Continued operation of the system under these loads is highly dangerous, presenting a severe risk of catastrophic component breakdown (e.g., rotor locking, scroll fracture), motor winding burnout, or electrical fires in the main control panel. Immediate action must be taken to isolate the system.
            
            * **Urgency**: Immediate (Within 1 hour).
            * **Current Health Score**: {health_score:.1f}/100.
            * **Assessed Risk Level**: CRITICAL.
            * **Primary Recommendations**: Complete system isolation, lock-out tag-out (LOTO), and manual technician inspection.
            
            ---
            
            ### 🛠️ Technical Troubleshooting Guide
            1. **Isolate Power**: De-energize the unit at the local disconnect box. Apply Lock-Out Tag-Out (LOTO) to the main circuit breaker to prevent accidental startup.
            2. **Pressure Equalization**: Attach digital manifold gauge set to high and low suction valves to measure system pressure differentials.
            3. **Inspect Bearings & Rotor**: Measure shaft axial and radial play using a dial indicator. Check the compressor oil sump and magnet plugs for metallic shavings or debris.
            4. **Clean Outdoor Coil Fins**: Visually inspect the condenser coils. Clear off debris, leaves, or scale deposits using compressed air or water wash.
            5. **Re-Test Current**: Briefly power on the system under controlled load while monitoring current draw on all phases to ensure it settles within nameplate limits.
            
            ---
            
            ### 🧰 Required Tools & Safety Checklist
            * **Tools Needed**: Laser Shaft Alignment kit, digital refrigerant manifold gauges, clamp-on multimeter, torque wrench, dial indicator.
            * **PPE Required**: Electrical insulated gloves (Class 00), protective face shield, safety goggles, steel-toe boots.
            * **Safety Rules**: Ensure a 2-person buddy system is active for all high-voltage panel checks. Verify zero-energy state before touching internal electrical components.
            
            ---
            
            ### 📅 Future Preventive Maintenance Schedule
            * **Short-Term**: Increase telemetry monitoring frequency to 5-minute intervals for the next 7 days to verify parameter stability.
            * **Mid-Term**: Schedule full compressor oil analysis and change the liquid line filter drier within 15 days.
            * **Long-Term**: Replace baseline vibration dampers on the mounting base and inspect anchor bolts.
            """)
        elif risk == "HIGH":
            st.markdown(f"""
            ## ⚠️ URGENT MAINTENANCE ACTION REPORT
            
            ### 📝 Executive Summary
            The HVAC system (ID: **{machine_id}**, Subsystem: **{ac_type}**) is exhibiting **HIGH operational risk and significant performance degradation**. Parameter drifts (such as rising temperatures, minor vibrations, or decreased airflow) indicate that the equipment is operating outside of its normal engineering tolerance window.
            
            While catastrophic failure is not immediate, the system's longevity is highly compromised. Operating under these conditions will accelerate wear on the compressor, degrade lubricant quality, and increase energy consumption by up to 40%. Maintenance must be performed within 24 hours to prevent escalation to critical/emergency status.
            
            * **Urgency**: Urgent (Within 24 hours).
            * **Current Health Score**: {health_score:.1f}/100.
            * **Assessed Risk Level**: HIGH.
            * **Primary Recommendations**: Schedule technician team, clean condenser coils, and check refrigerant charge.
            
            ---
            
            ### 🛠️ Technical Troubleshooting Guide
            1. **Filter Review**: Check primary and secondary air filters; replace immediately if pressure drop exceeds 150 Pa.
            2. **Leak Detection**: Use electronic leak detector or bubble test along all joint seals, coils, and service valves.
            3. **Inspect Belt/Coupling**: Inspect motor-blower drive belt tension, check alignment of pulleys, and adjust as needed.
            4. **Coil Inspection**: Spray foam cleaner on the outdoor condenser fins, let sit for 10 minutes, and wash down with low-pressure water.
            
            ---
            
            ### 🧰 Required Tools & Safety Checklist
            * **Tools Needed**: Electronic leak detector, fin comb tool, replacement MERV 13 filters, chemical foam spray.
            * **PPE Required**: Safety glasses, nitrile chemical-resistant gloves, dust respirator mask.
            * **Safety Rules**: Ensure unit is isolated before checking belt tension. Use proper eye protection during chemical coil cleaning.
            
            ---
            
            ### 📅 Future Preventive Maintenance Schedule
            * **Short-Term**: Re-check system parameters via the dashboard after 24 hours of operation post-service.
            * **Mid-Term**: Schedule comprehensive diagnostic test in the next monthly service.
            """)
        elif risk == "MEDIUM":
            st.markdown(f"""
            ## ℹ️ PRECAUTIONARY MAINTENANCE ACTION REPORT
            
            ### 📝 Executive Summary
            The HVAC system (ID: **{machine_id}**, Subsystem: **{ac_type}**) is showing **MEDIUM risk status with minor parameter deviations**. Operating parameters indicate slight deviations from the baseline (such as mild overheating or high humidity levels).
            
            Currently, the system is performing its primary cooling function, and there is no immediate danger to the equipment. However, these deviations indicate early stages of component aging or dirty filter/coil states. If left unaddressed for multiple weeks, these minor issues will slowly compound, leading to higher wear rates and potential premature failure.
            
            * **Urgency**: Routine (Within 7 days).
            * **Current Health Score**: {health_score:.1f}/100.
            * **Assessed Risk Level**: MEDIUM.
            * **Primary Recommendations**: Clean air intake filters, tighten electrical connections, and monitor telemetry.
            
            ---
            
            ### 🛠️ Technical Troubleshooting Guide
            1. **General Cleaning**: Clear debris, dirt, and leaves from the outdoor condenser unit's vicinity to ensure clear intake.
            2. **Tighten Fasteners**: Inspect electrical terminal connections inside the control box and tighten loose screw terminations to spec torque.
            3. **Check Damper**: Manually cycle the fresh air and return air dampers to confirm full range of motion.
            
            ---
            
            ### 🧰 Required Tools & Safety Checklist
            * **Tools Needed**: Screwdriver set, electrical contact cleaner spray, basic hand tools.
            * **PPE Required**: Safety glasses, standard work gloves.
            * **Safety Rules**: Shut off the local circuit breaker before opening the electrical control cabinet.
            
            ---
            
            ### 📅 Future Preventive Maintenance Schedule
            * **Short-Term**: Monitor telemetry on the sensor tracking page weekly.
            * **Mid-Term**: Perform standard quarterly checkups.
            """)
        else:
            st.markdown(f"""
            ## ✅ NOMINAL STATUS REPORT
            
            ### 📝 Executive Summary
            The HVAC system (ID: **{machine_id}**, Subsystem: **{ac_type}**) is operating under **NOMINAL/LOW risk conditions**. All monitored variables, electrical currents, pressures, and temperatures are well within their design limits.
            
            There are no mechanical or physical anomalies present. The system is operating at peak thermodynamic efficiency, drawing normal power, and maintaining excellent cooling performance. No corrective or immediate troubleshooting actions are needed at this stage.
            
            * **Urgency**: Nominal.
            * **Current Health Score**: {health_score:.1f}/100.
            * **Assessed Risk Level**: LOW.
            * **Primary Recommendations**: Maintain standard operating procedures and sensor logging.
            
            ---
            
            ### 🛠️ Technical Troubleshooting Guide
            * No active faults to troubleshoot. 
            * Run a manual diagnostic self-test to verify sensor calibration.
            
            ---
            
            ### 🧰 Required Tools & Safety Checklist
            * **Tools Needed**: None.
            * **PPE Required**: Standard safety boots.
            * **Safety Rules**: Standard safety procedures apply.
            
            ---
            
            ### 📅 Future Preventive Maintenance Schedule
            * **Next Inspection**: Schedule standard monthly preventive maintenance in 30 days.
            """)