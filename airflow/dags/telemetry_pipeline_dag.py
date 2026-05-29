from airflow import DAG

from airflow.operators.python import PythonOperator

from datetime import datetime, timedelta

import psycopg2

# =========================================
# DATABASE CONFIG
# =========================================

DB_CONFIG = {

    "host": "host.docker.internal",

    "database": "telemetry_db",

    "user": "postgres",

    "password": "root1234",

    "port": "5432"

}

# =========================================
# TASK 1
# CHECK CRITICAL MACHINES
# =========================================

def check_critical_machines():

    connection = psycopg2.connect(**DB_CONFIG)

    cursor = connection.cursor()

    query = """

    SELECT

        machine_id,
        health_score,
        failure_probability,
        risk_level

    FROM telemetry_data

    WHERE risk_level = 'CRITICAL'

    ORDER BY timestamp DESC

    LIMIT 10

    """

    cursor.execute(query)

    rows = cursor.fetchall()

    print("\n🚨 CRITICAL MACHINES\n")

    if len(rows) == 0:

        print("✅ No critical machines detected")

    else:

        for row in rows:

            print(f"""

Machine ID           : {row[0]}
Health Score        : {row[1]}
Failure Probability : {row[2]}
Risk Level          : {row[3]}

""")

    cursor.close()

    connection.close()

# =========================================
# TASK 2
# DAILY REPORT
# =========================================

def generate_daily_report():

    connection = psycopg2.connect(**DB_CONFIG)

    cursor = connection.cursor()

    query = """

    SELECT

        COUNT(*),

        AVG(temperature),

        AVG(vibration),

        AVG(health_score)

    FROM telemetry_data

    """

    cursor.execute(query)

    result = cursor.fetchone()

    print("\n📊 DAILY TELEMETRY REPORT\n")

    print(f"Total Records     : {result[0]}")

    print(f"Average Temp      : {result[1]:.2f}")

    print(f"Average Vibration : {result[2]:.2f}")

    print(f"Average Health    : {result[3]:.2f}")

    cursor.close()

    connection.close()

# =========================================
# DEFAULT DAG CONFIG
# =========================================

default_args = {

    "owner": "prathiksha",

    "depends_on_past": False,

    "retries": 1,

    "retry_delay": timedelta(minutes=1)

}

# =========================================
# DAG
# =========================================

dag = DAG(

    dag_id="telemetry_pipeline",

    default_args=default_args,

    description="Industrial telemetry monitoring pipeline",

    start_date=datetime(2025, 1, 1),

    schedule_interval="*/1 * * * *",

    catchup=False

)

# =========================================
# TASKS
# =========================================

check_task = PythonOperator(

    task_id="check_critical_machines",

    python_callable=check_critical_machines,

    dag=dag

)

report_task = PythonOperator(

    task_id="generate_daily_report",

    python_callable=generate_daily_report,

    dag=dag

)

# =========================================
# PIPELINE FLOW
# =========================================

check_task >> report_task