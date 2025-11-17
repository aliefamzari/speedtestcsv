FROM python:3.11-slim

# Install dependencies
RUN apt-get update && apt-get install -y \
    curl \
    gnupg \
    iputils-ping \
    && rm -rf /var/lib/apt/lists/*

# Install Ookla Speedtest CLI
RUN curl -s https://packagecloud.io/install/repositories/ookla/speedtest-cli/script.deb.sh | bash && \
    apt-get update && \
    apt-get install -y speedtest && \
    rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install --no-cache-dir influxdb-client

# Create app directory
WORKDIR /app

# Copy the speedtest script
COPY speedtest_influx.py /app/

# Make script executable
RUN chmod +x /app/speedtest_influx.py

# Run the script
CMD ["python3", "/app/speedtest_influx.py"]
