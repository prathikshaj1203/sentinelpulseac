FROM python:3.11-slim

WORKDIR /app

# Install system dependencies, Nginx, and Grafana
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget \
    ca-certificates \
    gnupg2 \
    nginx \
    libfontconfig1 \
    musl \
    && wget -q https://dl.grafana.com/oss/release/grafana_10.4.2_amd64.deb \
    && dpkg -i grafana_10.4.2_amd64.deb \
    && rm grafana_10.4.2_amd64.deb \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements.txt and install python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Copy custom Nginx configuration
COPY nginx.conf /etc/nginx/nginx.conf

# Copy Grafana dashboards & provisioning folders
COPY grafana/provisioning/ /etc/grafana/provisioning/
COPY grafana/dashboards/ /etc/grafana/dashboards/

# Create and grant open permissions for all run directories to bypass Hugging Face non-root restrictions
RUN mkdir -p /var/lib/grafana /var/log/grafana /etc/grafana /var/lib/nginx /var/log/nginx /var/run /run && \
    chmod -R 777 /var/lib/grafana /var/log/grafana /etc/grafana /var/lib/nginx /var/log/nginx /var/run /run /app

# Set default python encoding and unbuffered logging
ENV PYTHONIOENCODING=utf-8
ENV PYTHONUNBUFFERED=1

# Make start.sh executable and set it as entrypoint
RUN chmod +x start.sh
CMD ["bash", "start.sh"]

