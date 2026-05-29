#!/bin/bash

# Start the validated consumer in the background
echo "Starting Telemetry Consumer..."
python kafka/validated_consumer.py &

# Start the telemetry producer in the background
echo "Starting Telemetry Producer..."
python kafka/producer.py &

# Start the Streamlit app in the foreground on port 7860 (required by Hugging Face)
echo "Starting Streamlit App on port 7860..."
python -m streamlit run dashboards/Login.py --server.port 7860 --server.address 0.0.0.0
