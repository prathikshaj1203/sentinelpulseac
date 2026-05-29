# ───────────────────────────────────────────────────
# PROJECT   : SentinelPulse AI – Real-Time Predictive Maintenance System for Industrial Air Compressors
# FILE      : train_anomaly_model.py
# AUTHOR    : PRATHIKSHA J
# INTERN ID : SIT067
# DIVISION  : Software & AI Division – Stacia Corp
# MENTOR    : Mr. Lakshman P V (Chief Operational Officer)
# DATE      : 29-05-2026
# VERSION   : v1.0
# ───────────────────────────────────────────────────
# DESCRIPTION:
# Trains an unsupervised Isolation Forest model to detect HVAC operation anomalies on scale features.
# ───────────────────────────────────────────────────
# DEPENDENCIES:
# pandas, joblib, scikit-learn
# ───────────────────────────────────────────────────
# USAGE:
# python ai_models/train_anomaly_model.py
# ═══════════════════════════════════════════════════

import pandas as pd
import joblib

from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

# =========================================
# LOAD DATASET
# =========================================

df = pd.read_csv(

    "master_hvac_dataset.csv"

)

# =========================================
# FEATURES
# =========================================

features = [

    "rpm",
    "motor_power",
    "torque",
    "outlet_pressure_bar",
    "air_flow",
    "noise_db",
    "outlet_temp",
    "oil_tank_temp",
    "vibration",
    "humidity"

]

X = df[features]

# =========================================
# SCALE DATA
# =========================================

scaler = StandardScaler()

X_scaled = scaler.fit_transform(X)

# =========================================
# TRAIN ISOLATION FOREST
# =========================================

model = IsolationForest(

    contamination=0.05,

    random_state=42

)

model.fit(X_scaled)

# =========================================
# SAVE MODEL
# =========================================

joblib.dump(

    model,

    "anomaly_model.pkl"

)

joblib.dump(

    scaler,

    "anomaly_scaler.pkl"

)

print(

    "✅ Anomaly model trained successfully"

)