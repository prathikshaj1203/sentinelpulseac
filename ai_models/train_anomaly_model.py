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