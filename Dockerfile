FROM python:3.11-slim

WORKDIR /app

# Copy requirements.txt and install python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application files
COPY . .

# Set default python encoding and unbuffered logging
ENV PYTHONIOENCODING=utf-8
ENV PYTHONUNBUFFERED=1

# Make start.sh executable and set it as entrypoint
RUN chmod +x start.sh
CMD ["bash", "start.sh"]

