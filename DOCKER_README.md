# Speedtest Monitor with Grafana Dashboard

Automated internet speed testing with live Grafana visualization running in Docker. Tests your connection periodically and displays real-time metrics including download/upload speeds, latency, jitter, and packet loss.

## ?? Features

- **Automated Speed Testing**: Runs Ookla Speedtest CLI on a configurable schedule (default: every hour)
- **Live Grafana Dashboard**: Real-time visualization with:
  - Current speed gauges (Download/Upload/Latency)
  - Historical trends (24h, 7 days, 30 days)
  - Daily and monthly averages
  - Packet loss tracking
  - Recent test results table
- **InfluxDB Storage**: Time-series database for efficient data storage and querying
- **Docker Compose**: One-command deployment
- **Portainer Compatible**: Easy management through Portainer UI

## ?? Prerequisites

- Docker and Docker Compose installed
- (Optional) Portainer for web-based management

## ??? Architecture

```
???????????????????     ???????????????????     ???????????????????
?  Speedtest      ???????   InfluxDB      ???????    Grafana      ?
?  Container      ?     ?   (Database)    ?     ?   (Dashboard)   ?
?  (Python)       ?     ?   Port: 8086    ?     ?   Port: 3000    ?
???????????????????     ???????????????????     ???????????????????
```

## ?? Quick Start

### Option 1: Docker Compose (Command Line)

1. **Clone or download this repository**

2. **Start all services:**
   ```bash
   docker-compose up -d
   ```

3. **Access Grafana:**
   - URL: http://localhost:3000
   - Username: `admin`
   - Password: `admin` (you'll be prompted to change it)

4. **The dashboard will be automatically loaded** and data will start appearing after the first speedtest run (within 1 hour by default)

### Option 2: Portainer Deployment

1. **In Portainer, go to Stacks ? Add Stack**

2. **Upload or paste the `docker-compose.yml` file**

3. **Deploy the stack**

4. **Access Grafana** at http://localhost:3000 (or your server's IP)

## ?? Configuration

### Change Speedtest Interval

Edit the `SPEEDTEST_INTERVAL` environment variable in `docker-compose.yml`:

```yaml
environment:
  - SPEEDTEST_INTERVAL=3600  # in seconds (3600 = 1 hour)
```

Common intervals:
- Every 30 minutes: `1800`
- Every hour: `3600` (default)
- Every 2 hours: `7200`
- Every 15 minutes: `900`

### Change Default Passwords

**Important:** Change these for production use!

In `docker-compose.yml`:

```yaml
# InfluxDB
environment:
  - DOCKER_INFLUXDB_INIT_PASSWORD=your-secure-password
  - DOCKER_INFLUXDB_INIT_ADMIN_TOKEN=your-secure-token

# Grafana
environment:
  - GF_SECURITY_ADMIN_PASSWORD=your-secure-password
```

Also update the token in `grafana/provisioning/datasources/influxdb.yml`:
```yaml
secureJsonData:
  token: your-secure-token  # Match the InfluxDB token
```

### Ports Configuration

If ports 3000 or 8086 are already in use, change them in `docker-compose.yml`:

```yaml
services:
  grafana:
    ports:
      - "3001:3000"  # Change 3001 to your preferred port
  
  influxdb:
    ports:
      - "8087:8086"  # Change 8087 to your preferred port
```

## ?? Dashboard Features

The pre-configured dashboard includes:

### Current Status
- **Download Speed Gauge**: Real-time download speed with color thresholds
- **Upload Speed Gauge**: Real-time upload speed
- **Latency Gauge**: Current ping latency
- **Packet Loss**: Trend over time

### Time Series Graphs
- **Download & Upload Over Time**: Combined view with statistics (mean/max/min)
- **Latency & Jitter**: Network quality metrics
- **Daily Averages**: Last 7 days bar chart
- **Monthly Trends**: Last 30 days overview

### Tables
- **Recent Test Results**: Latest speedtest data

### Auto-Refresh
Dashboard auto-refreshes every 30 seconds to show the latest data.

## ?? Troubleshooting

### No data in Grafana?

1. **Check if speedtest container is running:**
   ```bash
   docker-compose logs speedtest
   ```

2. **Verify InfluxDB connection:**
   ```bash
   docker-compose logs influxdb
   ```

3. **Wait for first test to complete** (up to 1 hour with default settings)

### Speedtest fails?

Check the logs:
```bash
docker-compose logs -f speedtest
```

Common issues:
- No internet connection
- Firewall blocking Speedtest CLI
- Speedtest servers unavailable

### InfluxDB connection errors?

Ensure the token matches in:
- `docker-compose.yml` (INFLUXDB_TOKEN)
- `grafana/provisioning/datasources/influxdb.yml`

### Reset everything?

```bash
docker-compose down -v  # Warning: This deletes all data!
docker-compose up -d
```

## ?? File Structure

```
.
??? docker-compose.yml                          # Main orchestration file
??? speedtest/
?   ??? Dockerfile                              # Speedtest container image
?   ??? speedtest_influx.py                     # Python script for testing
??? grafana/
?   ??? provisioning/
?   ?   ??? datasources/
?   ?   ?   ??? influxdb.yml                    # InfluxDB datasource config
?   ?   ??? dashboards/
?   ?       ??? dashboard.yml                   # Dashboard provisioning
?   ??? dashboards/
?       ??? speedtest-dashboard.json            # Pre-built dashboard
??? README.md                                    # This file
```

## ?? Stopping Services

```bash
docker-compose down
```

To remove all data (volumes):
```bash
docker-compose down -v
```

## ?? Updating

Pull the latest changes and restart:
```bash
git pull  # if using git
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

## ?? Accessing Data

### Grafana
- **URL**: http://localhost:3000
- **Default credentials**: admin/admin

### InfluxDB UI
- **URL**: http://localhost:8086
- **Username**: admin
- **Password**: adminpassword123 (change in docker-compose.yml)

## ?? Security Notes

For production deployments:
1. Change all default passwords
2. Use environment files for secrets (`.env`)
3. Enable HTTPS with reverse proxy (nginx/Traefik)
4. Restrict port access with firewall rules
5. Regular backups of InfluxDB data

## ?? Data Retention

By default, InfluxDB keeps all data. To set retention policies:

1. Access InfluxDB UI at http://localhost:8086
2. Go to **Load Data ? Buckets**
3. Edit the `speedtest` bucket
4. Set retention period (e.g., 30 days, 90 days, etc.)

## ?? Contributing

Feel free to submit issues or pull requests for improvements!

## ?? License

MIT License - See original LICENSE file

## ?? Author

Alif Amzari Mohd Azamee

---

## ? Quick Command Reference

```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f speedtest
docker-compose logs -f grafana
docker-compose logs -f influxdb

# Restart a service
docker-compose restart speedtest

# Stop services
docker-compose down

# Stop and remove all data
docker-compose down -v

# Rebuild after changes
docker-compose build --no-cache
docker-compose up -d
```
