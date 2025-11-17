# Speedtest Monitor for Raspberry Pi

ARM-compatible Docker setup for automated internet speed testing with Grafana visualization on Raspberry Pi.

## ?? Raspberry Pi Compatibility

This setup uses ARM-compatible images:
- **InfluxDB 1.8** (arm32v7/influxdb:1.8)
- **Grafana 9.5.15** (supports ARM)
- **Custom Python speedtest container** (built on ARM)

## ?? Quick Start on Raspberry Pi

### 1. Clone the repository

```bash
cd ~
git clone https://github.com/aliefamzari/speedtestcsv.git
cd speedtestcsv
```

### 2. Start the stack

```bash
docker compose up -d
```

### 3. Access Grafana

Open your browser and go to:
```
http://your-raspberry-pi-ip:3000
```

**Default login:**
- Username: `admin`
- Password: `admin` (change on first login)

### 4. View the dashboard

The dashboard will be automatically loaded. Data will appear after the first speedtest runs (within 1 hour by default).

## ?? Configuration

### Change Test Interval

Edit `docker-compose.yml`:

```yaml
environment:
  - SPEEDTEST_INTERVAL=3600  # seconds (3600 = 1 hour)
```

Common intervals:
- Every 15 minutes: `900`
- Every 30 minutes: `1800`
- Every hour: `3600` (default)
- Every 2 hours: `7200`

Then restart:
```bash
docker compose restart speedtest
```

### Change Passwords

In `docker-compose.yml`:

```yaml
# InfluxDB
environment:
  - INFLUXDB_ADMIN_PASSWORD=your-new-password

# Speedtest service
environment:
  - INFLUXDB_PASSWORD=your-new-password  # Must match above
```

Also update `grafana/provisioning/datasources/influxdb.yml`:
```yaml
secureJsonData:
  password: your-new-password
```

Then rebuild:
```bash
docker compose down
docker compose up -d
```

## ?? Dashboard Features

- **Current Speed Gauges**: Download, Upload, Latency
- **24-hour Trends**: Download/Upload over time
- **Packet Loss Monitoring**: Track connection stability
- **Latency & Jitter**: Network quality metrics
- **Daily Averages**: See performance patterns
- **7-day History**: Week-long performance view

## ?? Troubleshooting

### Check container status

```bash
docker compose ps
```

### View logs

```bash
# All services
docker compose logs

# Specific service
docker compose logs -f speedtest
docker compose logs -f grafana
docker compose logs -f influxdb
```

### Speedtest not running?

```bash
# Check speedtest container
docker compose logs speedtest

# Restart speedtest
docker compose restart speedtest
```

### No data in Grafana?

1. Wait for first test (up to 1 hour)
2. Check speedtest logs: `docker compose logs speedtest`
3. Verify InfluxDB is running: `docker compose ps influxdb`
4. Check datasource in Grafana: Settings ? Data Sources

### Connection refused errors?

```bash
# Restart all services
docker compose restart

# If still failing, rebuild
docker compose down
docker compose up -d --build
```

### Out of memory?

For Raspberry Pi with limited RAM, you might need to reduce resource usage:

Add to `docker-compose.yml` under each service:
```yaml
deploy:
  resources:
    limits:
      memory: 256M  # Adjust as needed
```

## ?? File Structure

```
speedtestcsv/
??? docker-compose.yml              # Main configuration (ARM images)
??? speedtest/
?   ??? Dockerfile                  # ARM-compatible build
?   ??? speedtest_influx_v1.py      # Python script for InfluxDB 1.8
??? grafana/
?   ??? provisioning/
?   ?   ??? datasources/
?   ?   ?   ??? influxdb.yml        # InfluxDB 1.8 config
?   ?   ??? dashboards/
?   ?       ??? dashboard.yml
?   ??? dashboards/
?       ??? speedtest-dashboard-rpi.json  # ARM-optimized dashboard
??? RASPBERRY_PI_README.md          # This file
```

## ?? Updates

```bash
cd ~/speedtestcsv
git pull
docker compose down
docker compose up -d --build
```

## ?? Stop Services

```bash
# Stop (keep data)
docker compose down

# Stop and remove all data
docker compose down -v
```

## ?? Data Persistence

Data is stored in Docker volumes:
- `influxdb-data`: Speedtest results
- `grafana-data`: Dashboard configurations

To backup:
```bash
docker run --rm -v speedtestcsv_influxdb-data:/data -v $(pwd):/backup ubuntu tar czf /backup/influxdb-backup.tar.gz /data
```

## ??? Monitor Raspberry Pi Resources

While running, monitor your Pi:

```bash
# CPU and memory
htop

# Docker stats
docker stats

# Disk usage
df -h
```

## ? Performance Tips

1. **Use a good SD card** - Class 10 or better
2. **Consider SSD/USB boot** - Faster and more reliable
3. **Monitor temperature** - Ensure adequate cooling
4. **Adjust intervals** - Longer intervals = less load

## ?? Security

For production use:
1. Change default passwords
2. Use firewall rules to restrict access
3. Consider HTTPS with reverse proxy (nginx)
4. Keep system updated: `sudo apt update && sudo apt upgrade`

## ?? Access from Anywhere

### Option 1: Port Forwarding
Forward port 3000 on your router to your Raspberry Pi

### Option 2: Tailscale/WireGuard
Set up a VPN for secure remote access

### Option 3: Reverse Proxy
Use Cloudflare Tunnel or similar service

## ?? Support

If you encounter issues:
1. Check logs: `docker compose logs`
2. Verify internet connection
3. Ensure adequate disk space: `df -h`
4. Check for updates: `git pull`

## ?? License

MIT License

## ?? Author

Alif Amzari Mohd Azamee

---

**Tested on:**
- Raspberry Pi 3 Model B+
- Raspberry Pi 4
- Raspberry Pi Zero 2 W
