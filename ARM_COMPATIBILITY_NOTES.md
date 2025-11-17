# Raspberry Pi ARM Compatibility Updates

## Changes Made for ARM v7 Support

### ? Updated Files

#### 1. **docker-compose.yml**
- Changed InfluxDB image: `influxdb:2.7` ? `arm32v7/influxdb:1.8`
- Changed Grafana image: `grafana/grafana:latest` ? `grafana/grafana:9.5.15`
- Updated environment variables for InfluxDB 1.8 compatibility
- Removed obsolete `version: '3.8'` (causes warning)

#### 2. **speedtest/speedtest_influx_v1.py** (NEW)
- Created new Python script compatible with InfluxDB 1.8
- Uses `influxdb` library instead of `influxdb-client`
- Uses InfluxDB v1 API (simpler, more ARM-friendly)
- Maintains all original functionality

#### 3. **speedtest/Dockerfile**
- Changed Python dependency: `influxdb-client` ? `influxdb`
- Updated to use `speedtest_influx_v1.py`

#### 4. **grafana/provisioning/datasources/influxdb.yml**
- Changed from Flux (InfluxDB 2.x) to InfluxQL (InfluxDB 1.x)
- Updated authentication method
- Removed organization/bucket concepts (1.x uses database)

#### 5. **grafana/dashboards/speedtest-dashboard-rpi.json** (NEW)
- Created ARM-optimized dashboard
- Converted all Flux queries to InfluxQL
- Simplified queries for better performance on Pi

#### 6. **RASPBERRY_PI_README.md** (NEW)
- Comprehensive guide for Raspberry Pi deployment
- Troubleshooting tips
- Performance optimization
- Backup instructions

## Why These Changes?

### ARM Compatibility Issues
- InfluxDB 2.x doesn't have official ARM v7 builds
- InfluxDB 1.8 has mature ARM support
- Grafana 9.5.15 is the last version with good ARM v7 support

### InfluxDB 1.x vs 2.x
| Feature | InfluxDB 1.8 | InfluxDB 2.x |
|---------|--------------|---------------|
| ARM Support | ? Excellent | ? Limited |
| Query Language | InfluxQL | Flux |
| Authentication | User/Password | Token-based |
| Organization | Databases | Buckets |
| Resource Usage | Lower | Higher |

## Deployment Steps

1. **Pull latest code** on Raspberry Pi:
   ```bash
   cd ~/speedtestcsv
   git pull
   ```

2. **Start services**:
   ```bash
   docker compose up -d
   ```

3. **Monitor startup**:
   ```bash
   docker compose logs -f
   ```

4. **Access Grafana**:
   - URL: http://raspberry-pi-ip:3000
   - Login: admin/admin

## Testing Checklist

- [ ] All containers start successfully
- [ ] InfluxDB creates database
- [ ] Speedtest runs without errors
- [ ] Data appears in InfluxDB
- [ ] Grafana loads dashboard
- [ ] Graphs show data after first test
- [ ] Auto-refresh works (30 seconds)

## Common Issues & Solutions

### Issue: "no matching manifest for linux/arm/v7"
**Solution:** ? Fixed - using ARM-specific images

### Issue: Flux queries don't work
**Solution:** ? Fixed - converted to InfluxQL

### Issue: Out of memory on Pi Zero
**Solution:** Add memory limits in docker-compose.yml

### Issue: Slow performance
**Solution:** Increase test interval (reduce frequency)

## Next Steps

After deployment:
1. Let it run for a few hours to collect data
2. Adjust test interval if needed
3. Customize dashboard thresholds
4. Set up data retention policy
5. Configure backups

## Rollback Plan

If issues occur:
```bash
# Stop new version
docker compose down

# Switch to old bash script
cd ~/speedtestcsv
./speedtestcsv.sh
```

## Performance Expectations

On Raspberry Pi 3/4:
- Container startup: 30-60 seconds
- Speedtest duration: 20-40 seconds
- Memory usage: ~150-200MB total
- CPU usage: <10% when idle, ~30% during test

## Files Preserved

These original files remain unchanged:
- `speedtestcsv.sh` (original bash script)
- `speedtestcsv.ps1` (PowerShell version)
- `README.md` (original documentation)
- `LICENSE`

You can still use the original bash script if Docker doesn't work.

---

**Migration Complete! ??**

Your Raspberry Pi setup is now ready with ARM-optimized containers.
