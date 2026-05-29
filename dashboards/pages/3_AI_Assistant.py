import streamlit as st
import os
import time
from dotenv import load_dotenv
import google.generativeai as genai
from utils.ui import init_page, page_header

# =========================================
# ENVIRONMENT SETUP & AUTH (Must be first)
# =========================================
load_dotenv()
init_page("SentinelPulse AI - HVAC Assistant", required_role=["ADMIN", "TECHNICIAN"])

# Verify AI status
ai_key = os.getenv("GOOGLE_API_KEY")
use_ai = False

if ai_key:
    try:
        genai.configure(api_key=ai_key)
        use_ai = True
    except Exception:
        use_ai = False

# =========================================
# CHAT SESSION STATE
# =========================================
if "messages" not in st.session_state:
    st.session_state.messages = []

# =========================================
# LAYOUT HEADER & CLEAR BUTTON
# =========================================
col_title, col_btn = st.columns([0.8, 0.2])
with col_title:
    page_header("AI HVAC Assistant", "Industrial troubleshooting copilot")

with col_btn:
    st.markdown("<div style='margin-top: 25px;'></div>", unsafe_allow_html=True)
    if st.button("Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# Connection status message
if use_ai:
    st.info("AI Copilot: Connected to system engine.")
else:
    st.warning("AI Copilot: Running in Offline Local Knowledge Base Mode.")

# =========================================
# LOCAL KNOWLEDGE BASE (Fallback Engine)
# =========================================
def get_copilot_response_fallback(question, detailed=False):
    q = question.lower()
    if "vibration" in q:
        if detailed:
            return """
### 🛠️ Detailed Vibration Diagnostic Report
- **Equipment Component**: Motor rotor shaft & bearing assemblies.
- **Assessed Causes**:
  1. *Bearing Sleeve Wear*: Micro-fissures in internal races. (Severity: High)
  2. *Coupling Shaft Misalignment*: Dynamic imbalance during high-RPM cycles.
  3. *Structural Fatigue*: Mounting bolts loose or degraded damper pads.
- **Required Tools**: Laser alignment kit, calibrated torque wrench, vibration analyzer.
- **Estimated Repair Time**: 2.5 hours.
- **Recommended Actions**:
  1. Measure vibration signature using accelerometer to isolate bearing noise.
  2. Perform laser alignment to precision tolerance (<0.05 mm).
  3. Inspect and torque all foundation mounting bolts to 120 Nm.
  4. Replace damper isolation mounts if elasticity is compromised.
"""
        else:
            return """
### Possible Causes of High Vibration
- Bearing Wear: Degradation of internal bearings.
- Shaft Misalignment: Shift in motor/compressor couplings.
- Loose Mountings: Foundation bolts structural fatigue.

### Recommended Actions
1. Schedule bearing sleeve thickness ultrasound test.
2. Perform laser alignment inspection on rotor shaft.
3. Tighten mounting chassis bolts to spec torque.
"""
    elif "overheat" in q or "temp" in q:
        if detailed:
            return """
### 🌡️ Detailed Overheating Diagnostic Report
- **Equipment Component**: Condenser coils, intake filters, and refrigerant loop.
- **Assessed Causes**:
  1. *Airflow Impedance*: Filter dust saturation blocking cooling flow. (Severity: Medium)
  2. *Thermal Transfer Efficiency Drop*: Mineral scale or dirt build-up on condenser fins.
  3. *Refrigerant Charge Deviation*: Pressure imbalance (under/over charge).
- **Required Tools**: Digital manifold gauge set, fin comb, coil cleaning chemical wash.
- **Estimated Repair Time**: 1.5 hours.
- **Recommended Actions**:
  1. Replace primary air filters immediately (MERV 13 or higher).
  2. Apply foam coil cleaner to condenser coils, wash, and straighten fins.
  3. Verify refrigerant pressure and superheat values to confirm charge levels.
"""
        else:
            return """
### Possible Causes of Overheating
- Airflow Restriction: Clogged intake grilles or dirty air filters.
- Condenser Coils: Dirty surface prevents heat exchange.
- Refrigerant: Under-charged or over-charged system.

### Recommended Actions
1. Clear air path intakes and replace dirty primary filters.
2. Clean condenser coils using chemical spray wash.
3. Connect manifold gauges to verify refrigerant levels.
"""
    elif "pressure" in q:
        if detailed:
            return """
### ⚖️ Detailed Pressure Instability Report
- **Equipment Component**: Expansion valves, copper lines, and internal compressor valves.
- **Assessed Causes**:
  1. *Expansion Valve Scaling*: Restricted flow causing suction pressure drops. (Severity: High)
  2. *Refrigerant Line Leaks*: Micro-fractures from high vibration.
  3. *Compressor Valve Back-leakage*: Valve plate fatigue letting high-pressure gas back into suction line.
- **Required Tools**: Nitrogen cylinder, electronic leak detector, manifold gauge set.
- **Estimated Repair Time**: 3.0 hours.
- **Recommended Actions**:
  1. Measure temperature differential across the liquid line filter-drier.
  2. Conduct a pressurized nitrogen leak-down test at 150 PSI.
  3. Inspect compressor head and valves for leakage/wear.
"""
        else:
            return """
### Possible Causes of Pressure Instability
- Blockages: Expansion valve scaling.
- Leakage: Refrigerant lines cracked from vibration.
- Compressor Fault: Internal valves leaking back.

### Recommended Actions
1. Check temperature drop across liquid line dryer.
2. Conduct nitrogen pressure leak-testing on copper lines.
3. Check compressor current draw to verify pump capability.
"""
    elif "airflow" in q:
        if detailed:
            return """
### 💨 Detailed Airflow Obstruction Report
- **Equipment Component**: Blower motor, blower belt, and ducting system.
- **Assessed Causes**:
  1. *Belt Slippage / Degradation*: Worn blower fan belt. (Severity: Medium)
  2. *Capacitor Fatigue*: Blower motor capacitor failing to support torque.
  3. *Damper Obstruction*: Motorized damper actuator failing to open fully.
- **Required Tools**: Multimeter (with capacitance testing), replacement belt, tension gauge.
- **Estimated Repair Time**: 1.0 hours.
- **Recommended Actions**:
  1. Measure capacitance of the motor starting capacitor; replace if deviation exceeds 5%.
  2. Check fan belt tension; replace belt if cracked or glazing is present.
  3. Verify damper actuator power supply and manual override movement.
"""
        else:
            return """
### Possible Causes of Airflow Reduction
- Filter Blockage: Heavy dust buildup on filters.
- Blower Motor: Belt slipping or motor capacitor failing.
- Ducting: Damper closed or leakage.

### Recommended Actions
1. Replace primary and secondary filters.
2. Check fan belt tension and blower motor capacitor.
3. Inspect dampers and duct integrity.
"""
    else:
        if detailed:
            return """
### 🧠 SentinelPulse HVAC Copilot - Detailed System Diagnosis
I can provide deep technical insights and step-by-step resolution workflows for the following subsystems:
- **vibration**: Diagnostics for bearings, couplings, and mounting frames.
- **overheating / temp**: Diagnostics for heat exchangers, filters, and coolant.
- **pressure**: Diagnostics for valves, leaks, and compressor valves.
- **airflow**: Diagnostics for blowers, belts, and dampers.

*Please include any of these terms in your question for a comprehensive troubleshooting manual.*
"""
        else:
            return """
### SentinelPulse HVAC Copilot
I can help troubleshoot common HVAC issues. Please mention one of the following terms:
- vibration (bearings, alignment, loose bolts)
- overheating / temperature (airflow, coils, refrigerant)
- pressure (valves, leaks, compressor valves)
- airflow (filters, blowers, dampers)
"""

# Display Chat History
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Toggle for detailed response near text input
col_toggle, _ = st.columns([0.4, 0.6])
with col_toggle:
    detailed_mode = st.toggle(
        "Detailed View",
        value=False,
        help="Toggle on to get detailed technical steps, root causes, and repair actions. Toggle off for normal answer."
    )

# User prompt
prompt = st.chat_input("Ask HVAC troubleshooting questions...")

if prompt:
    # Check rate limit (minimum 5 seconds between user messages)
    current_time = time.time()
    last_time = st.session_state.get("last_message_time", 0.0)
    if current_time - last_time < 5.0:
        st.error("Rate limit exceeded. Please wait 5 seconds before sending another message.")
    else:
        st.session_state.last_message_time = current_time
        
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
            
        with st.chat_message("assistant"):
            response_placeholder = st.empty()
            
            if use_ai:
                try:
                    response_placeholder.markdown("Analyzing system parameters...")
                    
                    # Fetch recent active alerts to include as context
                    from utils.db import fetch_data
                    recent_alerts = fetch_data("SELECT machine_id, severity, message FROM alerts WHERE acknowledged = FALSE LIMIT 3")
                    
                    alert_context = ""
                    if not recent_alerts.empty:
                        alert_context = "\nActive system status context:\n"
                        for _, row in recent_alerts.iterrows():
                            alert_context += f"- Machine {row['machine_id']} reports {row['severity']}: {row['message']}\n"
                    
                    system_content = (
                        "You are the SentinelPulse AI HVAC Assistant, a state-of-the-art predictive maintenance copilot. "
                        "Provide precise, professional troubleshooting steps, possible root causes, and recommended actions "
                        "for industrial HVAC systems. Use Markdown formatting. "
                        "DO NOT USE ANY EMOJIS UNDER ANY CIRCUMSTANCES. Ensure all answers are clean and text-only."
                        f"{alert_context}"
                    )
                    
                    if detailed_mode:
                        system_content += (
                            "\n\nPlease provide a highly detailed, technical, step-by-step diagnostic breakdown. "
                            "Include possible root causes, concrete recommendations, estimated repair times, and required tools."
                        )
                    else:
                        system_content += (
                            "\n\nPlease provide a concise, direct, normal troubleshooting answer."
                        )
                    
                    model = genai.GenerativeModel(
                        model_name='gemini-1.5-flash',
                        system_instruction=system_content
                    )
                    
                    contents = []
                    # Add previous conversation context
                    for m in st.session_state.messages[-5:-1]:
                        role = "user" if m["role"] == "user" else "model"
                        contents.append({"role": role, "parts": [m["content"]]})
                    contents.append({"role": "user", "parts": [prompt]})
                    
                    generation_config = genai.types.GenerationConfig(
                        max_output_tokens=1500 if detailed_mode else 800,
                        temperature=0.3
                    )
                    
                    completion = model.generate_content(
                        contents,
                        generation_config=generation_config
                    )
                    response = completion.text
                    
                except Exception as e:
                    st.error("api fallback")
                    response = f"api fallback\n\n{get_copilot_response_fallback(prompt, detailed=detailed_mode)}"
            else:
                response = get_copilot_response_fallback(prompt, detailed=detailed_mode)
                
            response_placeholder.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})