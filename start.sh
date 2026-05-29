#!/bin/bash

# Setup environment variables defaults if not present
DB_HOST=${DB_HOST:-"localhost"}
DB_PORT=${DB_PORT:-5432}
DB_USER=${DB_USER:-"postgres"}
DB_NAME=${DB_NAME:-"telemetry_db"}
DB_PASSWORD=${DB_PASSWORD:-"root1234"}

# Create all Grafana runtime and configuration folders in /tmp to bypass read-only filesystems
echo "Setting up Grafana configurations in writeable /tmp..."
mkdir -p /tmp/grafana/data \
         /tmp/grafana/log \
         /tmp/grafana/plugins \
         /tmp/grafana/provisioning/datasources \
         /tmp/grafana/provisioning/dashboards \
         /tmp/grafana/dashboards

# Copy dashboard JSONs and provider configs from project to writeable /tmp
cp -r /app/grafana/dashboards/* /tmp/grafana/dashboards/

# Create dashboards.yml pointing to the writeable dashboards path
cat <<EOF > /tmp/grafana/provisioning/dashboards/dashboards.yml
apiVersion: 1

providers:
  - name: 'telemetry_dashboards'
    orgId: 1
    folder: ''
    type: file
    disableDeletion: false
    editable: true
    options:
      path: /tmp/grafana/dashboards
EOF

# Template the Grafana datasource file dynamically with active DB configurations inside /tmp
cat <<EOF > /tmp/grafana/provisioning/datasources/datasource.yml
apiVersion: 1

datasources:
  - name: telemetry_db
    type: postgres
    uid: telemetry_db
    access: proxy
    url: ${DB_HOST}:${DB_PORT}
    user: ${DB_USER}
    database: ${DB_NAME}
    jsonData:
      database: ${DB_NAME}
      sslmode: 'require'
      connMaxLifetime: 14400
      connMaxIdle: 2
      maxOpenConns: 5
      timescaledb: false
    secureJsonData:
      password: ${DB_PASSWORD}
    isDefault: true
EOF

# Export Grafana environment settings for seamless iframe embedding and subpath proxying
export GF_AUTH_ANONYMOUS_ENABLED=true
export GF_AUTH_ANONYMOUS_ORG_ROLE=Admin
export GF_SECURITY_ALLOW_EMBEDDING=true
export GF_SERVER_SERVE_FROM_SUB_PATH=true

if [ -n "$SPACE_ID" ]; then
    # Dynamically construct the absolute space domain for redirects
    subdomain=$(echo "$SPACE_ID" | tr '[:upper:]' '[:lower:]' | tr '/' '-')
    export GF_SERVER_ROOT_URL="https://${subdomain}.hf.space/grafana/"
else
    export GF_SERVER_ROOT_URL="http://localhost:3000/grafana/"
fi

# Export all path overrides to target /tmp
export GF_PATHS_DATA=/tmp/grafana/data
export GF_PATHS_LOGS=/tmp/grafana/log
export GF_PATHS_PLUGINS=/tmp/grafana/plugins
export GF_PATHS_PROVISIONING=/tmp/grafana/provisioning
export GF_PID_FILE_PATH=/tmp/grafana/grafana.pid

# Start the validated consumer in the background
echo "Starting Telemetry Consumer..."
python kafka/validated_consumer.py &

# Start the telemetry producer in the background
echo "Starting Telemetry Producer..."
python kafka/producer.py &

# Start Grafana Server in the background using the custom writeable paths
echo "Starting Grafana Server..."
/usr/sbin/grafana-server --homepath=/usr/share/grafana --config=/etc/grafana/grafana.ini &

# Start Streamlit App in the background on local port 8501 (Nginx will proxy to it)
echo "Starting Streamlit App..."
python -m streamlit run dashboards/Login.py --server.port 8501 --server.address 127.0.0.1 &

# Start Nginx in the foreground to tie them together on port 7860
echo "Starting Nginx Gateway..."
nginx -g "daemon off;"
