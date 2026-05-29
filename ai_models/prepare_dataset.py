import pandas as pd
import numpy as np

# =========================================
# LOAD AIR COMPRESSOR DATASET
# =========================================

compressor_df = pd.read_csv(

    "datasets/air_compressor.csv"

)

# =========================================
# LOAD METROPT3 DATASET
# =========================================

metro_df = pd.read_csv(

    "datasets/metropt3.csv",

    nrows=50000

)

# =========================================
# LOAD HVAC DATASET
# =========================================

hvac_df = pd.read_csv(

    "datasets/hvac.csv"

)

# =========================================
# SELECT IMPORTANT COLUMNS
# =========================================

compressor_df = compressor_df[[

    "rpm",

    "motor_power",

    "torque",

    "outlet_pressure_bar",

    "air_flow",

    "noise_db",

    "outlet_temp",

    "oil_tank_temp",

    "gaccx",

    "gaccy",

    "gaccz"

]]

# =========================================
# CREATE VIBRATION FEATURE
# =========================================

compressor_df["vibration"] = (

    abs(compressor_df["gaccx"]) +

    abs(compressor_df["gaccy"]) +

    abs(compressor_df["gaccz"])

) / 3

# =========================================
# DROP RAW ACCELEROMETER VALUES
# =========================================

compressor_df.drop(

    columns=[

        "gaccx",

        "gaccy",

        "gaccz"

    ],

    inplace=True

)

# =========================================
# PROCESS METROPT3 DATASET
# =========================================

metro_df = metro_df[[

    "TP2",

    "TP3",

    "Oil_temperature",

    "Motor_current",

    "DV_pressure"

]]

metro_df.columns = [

    "tp2_pressure",

    "tp3_pressure",

    "metro_oil_temp",

    "motor_current",

    "dv_pressure"

]

# =========================================
# PROCESS HVAC DATASET
# =========================================

hvac_df = hvac_df[[

    "T_Supply",

    "T_Return",

    "RH_Supply",

    "Power",

    "Energy"

]]

hvac_df.columns = [

    "supply_temp",

    "return_temp",

    "humidity",

    "hvac_power",

    "energy"

]

# =========================================
# MATCH DATASET LENGTHS
# =========================================

min_rows = min(

    len(compressor_df),

    len(metro_df),

    len(hvac_df)

)

compressor_df = compressor_df.head(min_rows)

metro_df = metro_df.head(min_rows)

hvac_df = hvac_df.head(min_rows)

# =========================================
# MERGE DATASETS
# =========================================

master_df = pd.concat(

    [

        compressor_df.reset_index(drop=True),

        metro_df.reset_index(drop=True),

        hvac_df.reset_index(drop=True)

    ],

    axis=1

)

# =========================================
# ADD AC TYPE
# =========================================

ac_types = [

    "Normal_AC",

    "Cassette_AC",

    "Centralized_AC"

]

master_df["ac_type"] = np.random.choice(

    ac_types,

    size=len(master_df)

)

# =========================================
# CREATE FAILURE SCORE
# =========================================

failure_score = (

    master_df["outlet_temp"] * 0.25 +

    master_df["vibration"] * 30 +

    master_df["outlet_pressure_bar"] * 2 +

    master_df["noise_db"] * 0.15 +

    master_df["motor_current"] * 0.2

)

master_df["failure_score"] = failure_score

# =========================================
# CREATE FAILURE LABEL
# =========================================

master_df["failure"] = np.where(

    master_df["failure_score"] > 70,

    1,

    0

)

# =========================================
# CREATE RISK LEVEL
# =========================================

conditions = [

    master_df["failure_score"] < 40,

    (master_df["failure_score"] >= 40) &
    (master_df["failure_score"] < 70),

    master_df["failure_score"] >= 70

]

choices = [

    "LOW",

    "MEDIUM",

    "HIGH"

]

master_df["risk_level"] = np.select(

    conditions,

    choices,

    default="LOW"

)

# =========================================
# SAVE MASTER DATASET
# =========================================

master_df.to_csv(

    "master_hvac_dataset.csv",

    index=False

)

# =========================================
# OUTPUT
# =========================================

print("\n✅ MASTER DATASET CREATED SUCCESSFULLY\n")

print(master_df.head())

print("\nSHAPE:\n")

print(master_df.shape)

print("\nCOLUMNS:\n")

print(master_df.columns.tolist())