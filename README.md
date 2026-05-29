---
title: SentinelPulse
emoji: ⚡
colorFrom: blue
colorTo: indigo
sdk: docker
app_port: 7860
pinned: false
---

# ⚡ SentinelPulse AI – Real-Time Predictive Maintenance System for Industrial Air Compressors

Developed for **Software & AI Division – Stacia Corp**  
* **Author:** Prathiksha J (Intern ID: SIT067)  
* **Mentor:** Mr. Lakshman P V (Chief Operational Officer)  
* **Date:** May 20, 2026  
* **Version:** v1.0

---

## 📋 1. What is this?

**SentinelPulse AI** is a containerized, real-time predictive maintenance and observability platform designed for industrial heating, ventilation, and air conditioning (HVAC) systems and rotary air compressors. 

By analyzing high-frequency telemetry streams (including chassis vibration, casing temperatures, motor power, and RPM), the platform detects physical anomalies early and predicts equipment failures before they occur. It provides technicians and administrators with a centralized control center to monitor health metrics, view AI diagnostics, issue work orders, and configure real-time notification alerts.

---

## 🛠️ 2. What does it do?

The platform consists of a distributed, event-driven architecture designed to process and visualize telemetry at scale:

* **Real-Time Data Ingestion**: Simulated sensor streams are pushed to a **Kafka** message broker.
* **AI Diagnostic Inference Engine**: A **validated Kafka consumer** processes incoming sensor records, computes health scores using supervised **XGBoost classifiers**, and isolates anomalous deviations using **Isolation Forest models**.
* **Observability Dashboards**: 
  * A custom **Streamlit Dashboard** featuring Role-Based Access Controls (RBAC) separating administrator and technician functions.
  * Real-time metrics visualization with interactive Plotly trend graphs.
  * Embedded **Grafana Observability Dashboards** showing system health and temporal logs.
* **Maintenance & AI Copilot**:
  * An integrated **Gemini 2.5 Flash** HVAC Copilot troubleshooting agent.
  * Automated email alert notifications dispatched directly to technicians upon critical anomaly events.
  * Comprehensive Maintenance Recommendation reports featuring step-by-step troubleshooting guidelines, required tooling, and safety checklists.

---

## 🧰 3. What do I need?

To run this platform locally or in a containerized environment, ensure the following requirements are met:

### System & Infrastructure Prerequisites
* **Docker & Docker Compose** (Recommended for single-command stack initialization)
* **Python 3.10+** (If running locally outside containers)
* **PostgreSQL 14+** (For relational time-series and alert logs)
* **Apache Kafka & Zookeeper** (For stream ingestion)

### Python Core Dependencies
* `streamlit` – Dashboard user interface
* `xgboost` – Failure prediction classifier
* `scikit-learn` – Feature scaling & anomaly detection (Isolation Forest)
* `kafka-python` – Message queuing connection
* `psycopg2-binary` & `sqlalchemy` – Database connectors
* `google-generativeai` – Gemini LLM interface
* `plotly` – Visual analytics charts

### Environment Configuration (`.env`)
Create a `.env` file in the root folder with the following variables configured:
```env
# Database Credentials
DB_HOST=localhost
DB_PORT=5432
DB_NAME=telemetry_db
DB_USER=postgres
DB_PASSWORD=root1234

# Kafka Configuration
KAFKA_BOOTSTRAP_SERVERS=localhost:9092

# Gemini API Integration
GOOGLE_API_KEY=your_gemini_api_key_here

# Notification Alerts (SMTP)
EMAIL_USER=your_sender_email@gmail.com
EMAIL_PASSWORD=your_app_password
ALERT_RECEIVER=operator_email@domain.com
```

---

## 🚀 4. How do I run it?

### Option A: The Docker Compose Way (Recommended)
This runs the entire stack—PostgreSQL, Kafka, Zookeeper, Grafana, Nginx, Streamlit, and the ML background workers—automatically.

1. **Build & Start all services**:
   ```bash
   docker-compose up --build -d
   ```
2. **Access the endpoints**:
   * Streamlit Dashboard: `http://localhost:7860`
   * Grafana Dashboard: `http://localhost:3000`

---

### Option B: Local Development Run (Manual)
If you wish to execute the services natively in your environment:

1. **Install Python virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Initialize Database**:
   Configure a local PostgreSQL database named `telemetry_db` and apply schema definitions.

3. **Start the AI Streaming Consumer**:
   ```bash
   python kafka/validated_consumer.py
   ```

4. **Start the Telemetry Simulator (Kafka Producer)**:
   ```bash
   python kafka/producer.py
   ```

5. **Launch the Dashboard**:
   ```bash
   streamlit run dashboards/Login.py
   ```

---

## 📂 5. Directory Structure

```
├── ai_models/               # ML models, dataset preparers, and training routines
│   ├── prepare_dataset.py   # Compiles master HVAC dataset
│   ├── train_model.py       # Trains XGBoost failure classification model
│   └── train_anomaly_model.py# Trains Isolation Forest anomaly detector
├── alerts/                  # Messaging interfaces for alerts
├── airflow/                 # Apache Airflow DAGs for telemetry reporting
├── dashboards/              # Streamlit Multi-page application
│   ├── Login.py             # User login portal & registration
│   ├── pages/               # Sidebar-accessible analytic panels
│   └── utils/               # Database, auth, and theme helpers
├── kafka/                   # Event streaming producer & consumer workers
│   ├── producer.py          # Data ingestion stream simulator
│   ├── validated_consumer.py# ML processing and database insertion worker
│   └── email_service.py     # SMTP alarm email notifier
├── nginx.conf               # Subpath reverse-proxy router
└── start.sh                 # Docker container orchestration script
```

---

## 🛡️ 6. Safety & Operational Rules
* **Buddy System**: A 2-person team is required when executing diagnostic work on high-voltage compartments.
* **LOTO**: Lock-Out Tag-Out protocols must be engaged on the circuit isolator before any physical or mechanical maintenance is performed on the compressor housing.
