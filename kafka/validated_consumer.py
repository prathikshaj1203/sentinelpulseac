# ───────────────────────────────────────────────────
# PROJECT   : SentinelPulse AI – Real-Time Predictive Maintenance System for Industrial Air Compressors
# FILE      : validated_consumer.py
# AUTHOR    : PRATHIKSHA J
# INTERN ID : SIT067
# DIVISION  : Software & AI Division – Stacia Corp
# MENTOR    : Mr. Lakshman P V (Chief Operational Officer)
# DATE      : 29-05-2026
# VERSION   : v1.0
# ───────────────────────────────────────────────────
# DESCRIPTION:
# Kafka consumer ingestion system running XGBoost model evaluations, raising alerts, and writing metrics to PostgreSQL.
# ───────────────────────────────────────────────────
# DEPENDENCIES:
# kafka-python, json, psycopg2, os, ssl, joblib, pandas, numpy, dotenv, email_service
# ───────────────────────────────────────────────────
# USAGE:
# python kafka/validated_consumer.py
# ═══════════════════════════════════════════════════

from kafka import KafkaConsumer
import json
import psycopg2
import os
import ssl
import joblib
import pandas as pd
import numpy as np
from dotenv import load_dotenv
from email_service import send_alert_email
load_dotenv()
connection = psycopg2.connect(

    host=os.getenv("DB_HOST"),

    database=os.getenv("DB_NAME"),

    user=os.getenv("DB_USER"),

    password=os.getenv("DB_PASSWORD"),

    port=os.getenv("DB_PORT")

)

cursor = connection.cursor()

# =========================================
# BASE DIRECTORY
# =========================================

BASE_DIR = os.path.dirname(

    os.path.dirname(

        os.path.abspath(__file__)

    )

)

# =========================================
# LOAD MAIN AI MODEL
# =========================================

model = joblib.load(

    os.path.join(

        BASE_DIR,

        "ai_models",

        "compressor_model.pkl"

    )

)

scaler = joblib.load(

    os.path.join(

        BASE_DIR,

        "ai_models",

        "scaler.pkl"

    )

)

encoder = joblib.load(

    os.path.join(

        BASE_DIR,

        "ai_models",

        "encoder.pkl"

    )

)

# =========================================
# LOAD ANOMALY MODEL
# =========================================

anomaly_model = joblib.load(

    os.path.join(

        BASE_DIR,

        "ai_models",

        "anomaly_model.pkl"

    )

)

anomaly_scaler = joblib.load(

    os.path.join(

        BASE_DIR,

        "ai_models",

        "anomaly_scaler.pkl"

    )

)

# =========================================
# KAFKA CONSUMER
# =========================================

kafka_kwargs = {
    'bootstrap_servers': os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092'),
    'value_deserializer': lambda x: json.loads(x.decode("utf-8"))
}

if os.getenv('KAFKA_USERNAME') and os.getenv('KAFKA_PASSWORD'):
    kafka_kwargs['security_protocol'] = os.getenv('KAFKA_SECURITY_PROTOCOL', 'SASL_SSL')
    kafka_kwargs['sasl_mechanism'] = os.getenv('KAFKA_SASL_MECHANISM', 'SCRAM-SHA-256')
    kafka_kwargs['sasl_plain_username'] = os.getenv('KAFKA_USERNAME')
    kafka_kwargs['sasl_plain_password'] = os.getenv('KAFKA_PASSWORD')
    
    # Bypass certificate verification
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    kafka_kwargs['ssl_context'] = ssl_context

consumer = KafkaConsumer("air_compressor_telemetry", **kafka_kwargs)

print("\n🟢 AI Consumer Listening...\n")

# =========================================
# ROOT CAUSE ANALYSIS
# =========================================

def analyze_root_cause(

    temperature,

    vibration,

    pressure,

    airflow,

    motor_power

):

    causes = []

    # =====================================
    # TEMPERATURE ANALYSIS
    # =====================================

    if temperature > 82:

        causes.append(

            "High compressor temperature detected"

        )

    # =====================================
    # VIBRATION ANALYSIS
    # =====================================

    if vibration > 1.3:

        causes.append(

            "Possible bearing instability due to excessive vibration"

        )

    # =====================================
    # PRESSURE ANALYSIS
    # =====================================

    if pressure > 1.8:

        causes.append(

            "Abnormal outlet pressure rise observed"

        )

    # =====================================
    # AIRFLOW ANALYSIS
    # =====================================

    if airflow < 306:

        causes.append(

            "Restricted airflow or duct blockage suspected"

        )

    # =====================================
    # POWER ANALYSIS
    # =====================================

    if motor_power > 1800:

        causes.append(

            "Motor overload condition detected"

        )

    # =====================================
    # DEFAULT
    # =====================================

    if len(causes) == 0:

        return "System operating normally"

    return " | ".join(causes)


# =========================================
# PROCESS STREAM
# =========================================

running_states = {}

for message in consumer:

    data = message.value

    try:

        # =================================
        # EXTRACT TELEMETRY
        # =================================

        machine_id = str(

            data["machine_id"]

        )

        rpm = float(data["rpm"])

        motor_power = float(

            data["motor_power"]

        )

        torque = float(

            data["torque"]

        )

        outlet_pressure = float(

            data["outlet_pressure_bar"]

        )

        air_flow = float(

            data["air_flow"]

        )

        noise_db = float(

            data["noise_db"]

        )

        outlet_temp = float(

            data["outlet_temp"]

        )

        oil_temp = float(

            data["oil_tank_temp"]

        )

        vibration = float(

            data["vibration"]

        )

        tp2_pressure = float(

            data["tp2_pressure"]

        )

        tp3_pressure = float(

            data["tp3_pressure"]

        )

        metro_oil_temp = float(

            data["metro_oil_temp"]

        )

        motor_current = float(

            data["motor_current"]

        )

        dv_pressure = float(

            data["dv_pressure"]

        )

        supply_temp = float(

            data["supply_temp"]

        )

        return_temp = float(

            data["return_temp"]

        )

        humidity = float(

            data["humidity"]

        )

        hvac_power = float(

            data["hvac_power"]

        )

        energy = float(

            data["energy"]

        )

        ac_type = data["ac_type"]

        # =================================
        # ENCODE AC TYPE
        # =================================

        ac_type_encoded = encoder.transform(

            [ac_type]

        )[0]

        # =================================
        # MAIN MODEL FEATURES
        # =================================

        feature_columns = [

            "rpm",
            "motor_power",
            "torque",
            "outlet_pressure_bar",
            "air_flow",
            "noise_db",
            "outlet_temp",
            "oil_tank_temp",
            "vibration",
            "tp2_pressure",
            "tp3_pressure",
            "metro_oil_temp",
            "motor_current",
            "dv_pressure",
            "supply_temp",
            "return_temp",
            "humidity",
            "hvac_power",
            "energy",
            "ac_type"

        ]

        features = [[

            rpm,
            motor_power,
            torque,
            outlet_pressure,
            air_flow,
            noise_db,
            outlet_temp,
            oil_temp,
            vibration,
            tp2_pressure,
            tp3_pressure,
            metro_oil_temp,
            motor_current,
            dv_pressure,
            supply_temp,
            return_temp,
            humidity,
            hvac_power,
            energy,
            ac_type_encoded

        ]]

        features_df = pd.DataFrame(

            features,

            columns=feature_columns

        )

        # =================================
        # SCALE MAIN FEATURES
        # =================================

        scaled_features = scaler.transform(

            features_df

        )

        # =================================
        # MAIN MODEL PREDICTION
        # =================================

        prediction = model.predict(

            scaled_features

        )[0]

        probability = model.predict_proba(

            scaled_features

        )[0][1]

        failure_probability = float(

            probability * 100

        )

        # =================================
        # HEALTH SCORE
        # =================================

        health_score = max(

            0,

            100 - failure_probability

        )

        # =================================
        # APPLY REALISTIC SMOOTHING & NOISE
        # =================================
        import random
        if machine_id not in running_states:
            running_states[machine_id] = {
                "health_score": health_score,
                "failure_probability": failure_probability,
                "temperature": outlet_temp,
                "vibration": vibration,
                "pressure": outlet_pressure,
                "rpm": rpm,
                "power_usage": motor_power
            }
        
        state = running_states[machine_id]
        
        # Exponential Moving Average for smooth transitions
        state["health_score"] = state["health_score"] * 0.96 + health_score * 0.04
        
        # Add organic noise (jitter)
        state["health_score"] += random.uniform(-0.5, 0.5)
        state["health_score"] = max(0.0, min(100.0, state["health_score"]))
        
        # Match failure probability to health score organically
        state["failure_probability"] = 100.0 - state["health_score"] + random.uniform(-0.2, 0.2)
        state["failure_probability"] = max(0.0, min(100.0, state["failure_probability"]))
        
        state["temperature"] = state["temperature"] * 0.9 + outlet_temp * 0.1
        state["temperature"] += random.uniform(-0.3, 0.3)
        
        state["vibration"] = state["vibration"] * 0.9 + vibration * 0.1
        state["vibration"] = max(0.1, state["vibration"] + random.uniform(-0.01, 0.01))
        
        state["pressure"] = state["pressure"] * 0.9 + outlet_pressure * 0.1
        state["pressure"] = max(0.0, state["pressure"] + random.uniform(-0.02, 0.02))
        
        state["rpm"] = state["rpm"] * 0.9 + rpm * 0.1
        state["rpm"] = max(0.0, state["rpm"] + random.uniform(-4.0, 4.0))
        
        state["power_usage"] = state["power_usage"] * 0.9 + motor_power * 0.1
        state["power_usage"] = max(0.0, state["power_usage"] + random.uniform(-10.0, 10.0))
        
        # Assign back to variables for inserting
        health_score = state["health_score"]
        failure_probability = state["failure_probability"]
        outlet_temp = state["temperature"]
        vibration = state["vibration"]
        outlet_pressure = state["pressure"]
        rpm = state["rpm"]
        motor_power = state["power_usage"]

        # =================================
        # RISK LEVEL
        # =================================

        if failure_probability > 80:

            risk_level = "CRITICAL"

        elif failure_probability > 60:

            risk_level = "HIGH"

        elif failure_probability > 30:

            risk_level = "MEDIUM"

        else:

            risk_level = "LOW"

        root_cause = analyze_root_cause(

            outlet_temp,

            vibration,

            outlet_pressure,

            air_flow,

            motor_power

        )

        # =================================
        # ANOMALY FEATURES
        # =================================

        anomaly_features = [[

            rpm,
            motor_power,
            torque,
            outlet_pressure,
            air_flow,
            noise_db,
            outlet_temp,
            oil_temp,
            vibration,
            humidity

        ]]

        # =================================
        # SCALE ANOMALY FEATURES
        # =================================

        scaled_anomaly = anomaly_scaler.transform(

            anomaly_features

        )

        # =================================
        # ANOMALY PREDICTION
        # =================================

        anomaly_prediction = anomaly_model.predict(

            scaled_anomaly

        )[0]

        # =================================
        # ANOMALY STATUS
        # =================================

        if anomaly_prediction == -1:

            anomaly_status = "ANOMALY DETECTED"

        else:

            anomaly_status = "NORMAL"

        # =================================
        # INSERT TELEMETRY
        # =================================

        insert_query = """

        INSERT INTO telemetry_data (

            machine_id,
            temperature,
            vibration,
            pressure,
            rpm,
            power_usage,
            health_score,
            failure_probability,
            anomaly_status,
            risk_level,
            predicted_failure,
            root_cause

        )

        VALUES (

            %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s

        )

        """

        values = (

            machine_id,

            outlet_temp,

            vibration,

            outlet_pressure,

            int(rpm),

            motor_power,

            round(health_score, 2),

            round(failure_probability, 2),

            anomaly_status,

            risk_level,

            int(prediction),
            root_cause

        )

        cursor.execute(

            insert_query,

            values

        )

        connection.commit()


        # Check if there is already an active (unacknowledged) alert for this machine
        check_query = "SELECT COUNT(*) FROM alerts WHERE machine_id = %s AND acknowledged = FALSE"
        cursor.execute(check_query, (machine_id,))
        active_alert_count = cursor.fetchone()[0]

        if risk_level == "CRITICAL" and active_alert_count == 0:
            send_alert_email(
                machine_id,
                risk_level,
                failure_probability,
                outlet_temp,
                vibration
            )

            # =================================
            # ALERT GENERATION
            # =================================
            alert_query = """
            INSERT INTO alerts (
                machine_id,
                alert_type,
                severity,
                message
            )
            VALUES (%s, %s, %s, %s)
            """

            alert_message = f"""
Critical failure risk detected.

Temperature:
{outlet_temp:.2f}°C

Vibration:
{vibration:.2f}

Failure Probability:
{failure_probability:.2f}%
"""

            cursor.execute(
                alert_query,
                (
                    machine_id,
                    "Predictive Failure",
                    "CRITICAL",
                    alert_message
                )
            )
            connection.commit()
            print(f"ALERT GENERATED FOR {machine_id}")
        print("\n" + "=" * 60)

        print("TELEMETRY STORED")

        print("=" * 60)

        print(f"Machine ID          : {machine_id}")

        print(f"Failure Probability : {failure_probability:.2f}%")

        print(f"Health Score        : {health_score:.2f}")

        print(f"Risk Level          : {risk_level}")

        print(f"Anomaly Status      : {anomaly_status}")

        print(f"Prediction          : {prediction}")
        print(f"Root Cause         : {root_cause}")

    except Exception as e:

        connection.rollback()

        print("\nERROR PROCESSING TELEMETRY\n")

        print(e)