# ───────────────────────────────────────────────────
# PROJECT   : SentinelPulse AI – Real-Time Predictive Maintenance System for Industrial Air Compressors
# FILE      : db.py
# AUTHOR    : PRATHIKSHA J
# INTERN ID : SIT067
# DIVISION  : Software & AI Division – Stacia Corp
# MENTOR    : Mr. Lakshman P V (Chief Operational Officer)
# DATE      : 29-05-2026
# VERSION   : v1.0
# ───────────────────────────────────────────────────
# DESCRIPTION:
# Database layer offering safe connection pooling and SQLAlchemy engine setups for Streamlit widgets.
# ───────────────────────────────────────────────────
# DEPENDENCIES:
# psycopg2, pandas, os, sqlalchemy, dotenv
# ───────────────────────────────────────────────────
# USAGE:
# Imported into Streamlit pages or management scripts.
# ═══════════════════════════════════════════════════

import psycopg2
import pandas as pd
import os
from sqlalchemy import create_engine
from dotenv import load_dotenv
load_dotenv()
def get_engine():
    db_url = f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
    return create_engine(db_url)
def get_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        port=os.getenv("DB_PORT")
    )
def fetch_data(query, params=None):
    """Fetches data from the database into a Pandas DataFrame using SQLAlchemy."""
    engine = get_engine()
    with engine.connect() as conn:
        return pd.read_sql(query, conn, params=params)
def execute_query(query, values=None):
    """Executes a query (insert, update, delete) and commits the changes."""
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(query, values)
            connection.commit()