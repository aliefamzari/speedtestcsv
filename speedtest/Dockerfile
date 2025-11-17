FROM python:3.11-slim

# Install dependencies including build tools for compiling Python packages
RUN apt-get update && apt-get install -y \
    curl \
    gnupg \
    iputils-ping \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Ookla Speedtest CLI
RUN curl -s https://packagecloud.io/install/repositories/ookla/speedtest-cli/script.deb.sh | bash && \
    apt-get update && \
    apt-get install -y speedtest && \
    rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install --no-cache-dir influxdb

# Create app directory
WORKDIR /app

# Copy the speedtest script and import tool
COPY speedtest/speedtest_influx_v1.py /app/speedtest_influx.py
COPY import_csv_to_influx.py /app/import_csv_to_influx.py

# Make scripts executable
RUN chmod +x /app/speedtest_influx.py /app/import_csv_to_influx.py

# Set Python to run in unbuffered mode so logs appear immediately
ENV PYTHONUNBUFFERED=1

# Run the script
CMD ["python3", "-u", "/app/speedtest_influx.py"]
