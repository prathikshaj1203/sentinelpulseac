# ───────────────────────────────────────────────────
# PROJECT   : SentinelPulse AI – Real-Time Predictive Maintenance System for Industrial Air Compressors
# FILE      : analyze_datasets.py
# AUTHOR    : PRATHIKSHA J
# INTERN ID : SIT067
# DIVISION  : Software & AI Division – Stacia Corp
# MENTOR    : Mr. Lakshman P V (Chief Operational Officer)
# DATE      : 29-05-2026
# VERSION   : v1.0
# ───────────────────────────────────────────────────
# DESCRIPTION:
# Performs exploratory data analysis (EDA) on base CSV datasets to check columns, shape, and null values.
# ───────────────────────────────────────────────────
# DEPENDENCIES:
# pandas
# ───────────────────────────────────────────────────
# USAGE:
# python ai_models/analyze_datasets.py
# ═══════════════════════════════════════════════════

import pandas as pd

# =========================================
# DATASET PATHS
# =========================================

datasets = {

    "Air Compressor":
    "datasets/air_compressor.csv",

    "MetroPT3":
    "datasets/metropt3.csv",

    "HVAC":
    "datasets/hvac.csv",
}

# =========================================
# ANALYZE DATASETS
# =========================================

for name, path in datasets.items():

    print("\n" + "=" * 60)

    print(f"DATASET: {name}")

    print("=" * 60)

    try:

        df = pd.read_csv(path)

        print("\nFIRST 5 ROWS:\n")

        print(df.head())

        print("\nSHAPE:\n")

        print(df.shape)

        print("\nCOLUMNS:\n")

        print(df.columns.tolist())

        print("\nMISSING VALUES:\n")

        print(df.isnull().sum())

    except Exception as e:

        print(f"\nERROR LOADING {name}")

        print(e)