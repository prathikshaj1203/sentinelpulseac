-- =========================================
-- TELEMETRY TABLE
-- =========================================

CREATE TABLE telemetry_data (

    id SERIAL PRIMARY KEY,

    machine_id VARCHAR(50),

    temperature FLOAT,

    vibration FLOAT,

    pressure FLOAT,

    rpm INTEGER,

    power_usage FLOAT,

    health_score FLOAT,

    failure_probability FLOAT,

    anomaly_status VARCHAR(50),

    risk_level VARCHAR(50),

    predicted_failure INTEGER,

    root_cause TEXT,

    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP

);

-- =========================================
-- MANUAL INSPECTION TABLE
-- =========================================

CREATE TABLE manual_inspections (

    id SERIAL PRIMARY KEY,

    technician_name VARCHAR(100),

    machine_id VARCHAR(50),

    temperature FLOAT,

    vibration FLOAT,

    pressure FLOAT,

    noise_level FLOAT,

    oil_leakage INTEGER,

    overheating INTEGER,

    abnormal_smell INTEGER,

    health_score FLOAT,

    failure_probability FLOAT,

    predicted_failure INTEGER,

    risk_level VARCHAR(50),

    remarks TEXT,

    inspection_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP

);

-- =========================================
-- USERS TABLE
-- =========================================

CREATE TABLE users (

    id SERIAL PRIMARY KEY,

    username VARCHAR(100),

    password VARCHAR(100),

    role VARCHAR(50),

    full_name VARCHAR(100),

    department VARCHAR(100)

);

-- =========================================
-- INSERT SAMPLE USERS
-- =========================================

INSERT INTO users (

    username,
    password,
    role,
    full_name,
    department

)

VALUES

('admin', 'admin123', 'Admin', 'System Administrator', 'Operations'),

('tech1', 'tech123', 'Technician', 'Prathiksha', 'Maintenance');

-- =========================================
-- ALERTS TABLE
-- =========================================

CREATE TABLE alerts (

    id SERIAL PRIMARY KEY,

    machine_id VARCHAR(50),

    alert_type VARCHAR(50),

    severity VARCHAR(50),

    message TEXT,

    acknowledged BOOLEAN DEFAULT FALSE,

    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP

);

-- =========================================
-- WORK ORDERS TABLE
-- =========================================

CREATE TABLE work_orders (

    id SERIAL PRIMARY KEY,

    machine_id VARCHAR(50),

    issue_type VARCHAR(100),

    severity VARCHAR(50),

    assigned_to VARCHAR(100),

    status VARCHAR(50) DEFAULT 'OPEN',

    description TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    completed_at TIMESTAMP

);