# ───────────────────────────────────────────────────
# PROJECT   : SentinelPulse AI – Real-Time Predictive Maintenance System for Industrial Air Compressors
# FILE      : train_model.py
# AUTHOR    : PRATHIKSHA J
# INTERN ID : SIT067
# DIVISION  : Software & AI Division – Stacia Corp
# MENTOR    : Mr. Lakshman P V (Chief Operational Officer)
# DATE      : 29-05-2026
# VERSION   : v1.0
# ───────────────────────────────────────────────────
# DESCRIPTION:
# Trains a supervised XGBoost classification model to predict HVAC compressor failures.
# ───────────────────────────────────────────────────
# DEPENDENCIES:
# pandas, numpy, joblib, scikit-learn, xgboost
# ───────────────────────────────────────────────────
# USAGE:
# python ai_models/train_model.py
# ═══════════════════════════════════════════════════

import pandas as pd
import numpy as np
import joblib

from sklearn.model_selection import train_test_split

from sklearn.preprocessing import LabelEncoder
from sklearn.preprocessing import StandardScaler

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    classification_report,
    confusion_matrix
)

from xgboost import XGBClassifier

# =========================================
# LOAD DATASET
# =========================================

df = pd.read_csv(

    "master_hvac_dataset.csv"

)

# =========================================
# DROP UNUSED COLUMNS
# =========================================

X = df.drop(

    columns=[

        "failure",

        "risk_level",

        "failure_score"

    ]

)

y = df["failure"]

# =========================================
# ENCODE AC TYPE
# =========================================

encoder = LabelEncoder()

X["ac_type"] = encoder.fit_transform(

    X["ac_type"]

)

# =========================================
# SCALE FEATURES
# =========================================

scaler = StandardScaler()

X_scaled = scaler.fit_transform(X)

# =========================================
# TRAIN TEST SPLIT
# =========================================

X_train, X_test, y_train, y_test = train_test_split(

    X_scaled,

    y,

    test_size=0.2,

    random_state=42,

    stratify=y

)

# =========================================
# XGBOOST MODEL
# =========================================

model = XGBClassifier(

    n_estimators=250,

    max_depth=8,

    learning_rate=0.05,

    subsample=0.9,

    colsample_bytree=0.9,

    random_state=42,

    eval_metric="logloss"

)

# =========================================
# TRAIN MODEL
# =========================================

print("\n🟢 TRAINING MODEL...\n")

model.fit(

    X_train,

    y_train

)

# =========================================
# PREDICTIONS
# =========================================

y_pred = model.predict(

    X_test

)

# =========================================
# METRICS
# =========================================

accuracy = accuracy_score(

    y_test,

    y_pred

)

precision = precision_score(

    y_test,

    y_pred

)

recall = recall_score(

    y_test,

    y_pred

)

f1 = f1_score(

    y_test,

    y_pred

)

# =========================================
# OUTPUT RESULTS
# =========================================

print("\n" + "=" * 60)

print("MODEL PERFORMANCE")

print("=" * 60)

print(f"\nAccuracy  : {accuracy:.4f}")

print(f"Precision : {precision:.4f}")

print(f"Recall    : {recall:.4f}")

print(f"F1 Score  : {f1:.4f}")

print("\nCLASSIFICATION REPORT:\n")

print(

    classification_report(

        y_test,

        y_pred

    )

)

print("\nCONFUSION MATRIX:\n")

print(

    confusion_matrix(

        y_test,

        y_pred

    )

)

# =========================================
# FEATURE IMPORTANCE
# =========================================

importance_df = pd.DataFrame({

    "Feature": X.columns,

    "Importance": model.feature_importances_

})

importance_df = importance_df.sort_values(

    by="Importance",

    ascending=False

)

print("\nTOP IMPORTANT FEATURES:\n")

print(

    importance_df.head(10)

)

# =========================================
# SAVE MODEL
# =========================================

joblib.dump(

    model,

    "compressor_model.pkl"

)

joblib.dump(

    scaler,

    "scaler.pkl"

)

joblib.dump(

    encoder,

    "encoder.pkl"

)

print("\n✅ MODEL SAVED SUCCESSFULLY\n")