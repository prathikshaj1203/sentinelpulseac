from kafka import KafkaProducer

import pandas as pd
import json
import time
import os

# =========================================
# LOAD MASTER DATASET
# =========================================

BASE_DIR = os.path.dirname(

    os.path.dirname(

        os.path.abspath(__file__)

    )

)

DATASET_PATH = os.path.join(

    BASE_DIR,

    "ai_models",

    "master_hvac_dataset.csv"

)

df = pd.read_csv(

    DATASET_PATH

)

# =========================================
# KAFKA PRODUCER
# =========================================

kafka_kwargs = {
    'bootstrap_servers': os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092'),
    'value_serializer': lambda v: json.dumps(v).encode('utf-8')
}

if os.getenv('KAFKA_USERNAME') and os.getenv('KAFKA_PASSWORD'):
    kafka_kwargs['security_protocol'] = os.getenv('KAFKA_SECURITY_PROTOCOL', 'SASL_SSL')
    kafka_kwargs['sasl_mechanism'] = os.getenv('KAFKA_SASL_MECHANISM', 'SCRAM-SHA-256')
    kafka_kwargs['sasl_plain_username'] = os.getenv('KAFKA_USERNAME')
    kafka_kwargs['sasl_plain_password'] = os.getenv('KAFKA_PASSWORD')

producer = KafkaProducer(**kafka_kwargs)

# =========================================
# MACHINE IDS
# =========================================

machines = [

    "AC_101",

    "AC_102",

    "AC_103"

]

# =========================================
# STREAM TELEMETRY
# =========================================

print("\n🟢 Streaming REAL HVAC telemetry with independent machine offsets...\n")

# Offset indices so each machine runs on a different operational cycle phase
machine_indices = {
    "AC_101": 0,
    "AC_102": 333,
    "AC_103": 666
}

while True:
    for machine_id in machines:
        idx = machine_indices[machine_id]
        row = df.iloc[idx]

        telemetry = {
            "machine_id": machine_id,
            "rpm": float(row["rpm"]),
            "motor_power": float(row["motor_power"]),
            "torque": float(row["torque"]),
            "outlet_pressure_bar": float(row["outlet_pressure_bar"]),
            "air_flow": float(row["air_flow"]),
            "noise_db": float(row["noise_db"]),
            "outlet_temp": float(row["outlet_temp"]),
            "oil_tank_temp": float(row["oil_tank_temp"]),
            "vibration": float(row["vibration"]),
            "tp2_pressure": float(row["tp2_pressure"]),
            "tp3_pressure": float(row["tp3_pressure"]),
            "metro_oil_temp": float(row["metro_oil_temp"]),
            "motor_current": float(row["motor_current"]),
            "dv_pressure": float(row["dv_pressure"]),
            "supply_temp": float(row["supply_temp"]),
            "return_temp": float(row["return_temp"]),
            "humidity": float(row["humidity"]),
            "hvac_power": float(row["hvac_power"]),
            "energy": float(row["energy"]),
            "ac_type": row["ac_type"]
        }

        producer.send(
            "air_compressor_telemetry",
            telemetry
        )

        # Advance index for this specific machine
        machine_indices[machine_id] = (idx + 1) % len(df)

    print("\n" + "=" * 60)
    print("📡 TELEMETRY STREAMED FOR ALL MACHINES")
    print("=" * 60)

    time.sleep(3)