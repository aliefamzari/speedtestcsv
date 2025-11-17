# Importing Historical CSV Data to InfluxDB

This guide explains how to import your existing speedtest CSV files into the InfluxDB database.

## Data Format Comparison

**Your CSV Format:**
```csv
Time,ISP,Server_name,Server_id,Latency,Jitter,Packet_loss,Download,Upload,Download_bytes,Upload_bytes,Share_url,IP
2025-10-01T00:00:01+08:00,"AS9930 TTNET-MY","TIME MY - Kuala Lumpur","50737","3.154","0.116","0","23810327","26016745","291044964","311501652","https://...",202.184.155.18
```

**InfluxDB Format:**
- **Download/Upload**: CSV stores bytes/sec, InfluxDB stores Mbps
  - Conversion: `bytes/sec × 8 ÷ 1,000,000 = Mbps`
  - Example: `23810327 bytes/sec = 190.48 Mbps`
- **Latency/Jitter**: Both use milliseconds (no conversion needed)
- **Packet Loss**: Both use percentage
- **Metadata**: ISP, Server info stored as tags

## Import Methods

### Method 1: Import from Raspberry Pi (Recommended)

1. **Copy CSV files to your Pi:**
   ```bash
   # On your Pi, create a directory for CSV files
   mkdir -p ~/speedtestcsv
   
   # From your computer, copy files to Pi
   scp ~/speedtestcsv/*-result.csv pi@raspberry-pi-ip:~/speedtestcsv/
   ```

2. **Copy the import script to Pi:**
   ```bash
   # On your Pi, in the Docker project directory
   cd ~/speeddocker/speedtestcsv
   git pull  # Get the latest import script
   ```

3. **Run the import:**
   ```bash
   # Install influxdb library in the speedtest container
   docker compose exec speedtest pip install influxdb
   
   # Copy CSV files into the container
   docker cp ~/speedtestcsv speedtest-runner:/data/
   
   # Run the import script
   docker compose exec speedtest python3 /app/import_csv_to_influx.py /data/speedtestcsv/*.csv
   ```

### Method 2: Import via Docker Volume (Easier)

1. **Modify docker-compose.yml to add a volume:**
   ```yaml
   speedtest:
     volumes:
       - ./import_data:/import_data  # Add this line
   ```

2. **Copy files and import:**
   ```bash
   # On your Pi
   cd ~/speeddocker/speedtestcsv
   mkdir -p import_data
   
   # Copy your CSV files here (from wherever you have them)
   cp ~/speedtestcsv/*.csv import_data/
   
   # Restart container to mount the volume
   docker compose up -d speedtest
   
   # Run import
   docker compose exec speedtest python3 import_csv_to_influx.py /import_data/*.csv
   ```

### Method 3: Direct Database Import (Advanced)

If you have the CSV files on your computer, you can import directly:

```bash
# On your computer (Windows PowerShell)
cd "C:\path\to\your\csv\files"

# Install Python InfluxDB client
pip install influxdb

# Run import (point to your Pi's IP)
$env:INFLUXDB_HOST="192.168.1.xxx"  # Your Pi's IP
python import_csv_to_influx.py *.csv
```

## Expected Output

```
Connecting to InfluxDB at influxdb:8086
? Connected to InfluxDB

Found 30 CSV files to import
============================================================

Processing: 01-24-result.csv
  Found 744 records
  Date range: 2024-01-01T00:00:01 to 2024-01-31T23:00:01
  Wrote batch 1/1
  ? Successfully imported 744 records

Processing: 02-24-result.csv
  Found 696 records
  ...

============================================================
Import complete: 30/30 files imported successfully
Total records in database: 21,840
```

## Verify Import

After importing, verify the data:

```bash
# Check total records
docker compose exec influxdb influx -username admin -password adminpassword123 -database speedtest -execute 'SELECT COUNT(*) FROM speedtest'

# Check earliest data
docker compose exec influxdb influx -username admin -password adminpassword123 -database speedtest -execute 'SELECT * FROM speedtest ORDER BY time ASC LIMIT 1'

# Check latest data
docker compose exec influxdb influx -username admin -password adminpassword123 -database speedtest -execute 'SELECT * FROM speedtest ORDER BY time DESC LIMIT 1'
```

## Grafana Dashboard

After importing, go to Grafana and:
1. Set the time range to cover your historical data (e.g., "Last 2 years")
2. The graphs should now show your complete speedtest history
3. You'll see trends, averages, and patterns over the entire period

## Troubleshooting

**Error: "command not found: python3"**
- The import script is not in the container. Make sure you pulled the latest code.

**Error: "No module named 'influxdb'"**
- Run: `docker compose exec speedtest pip install influxdb`

**Error: "unable to parse authentication credentials"**
- Check your password in docker-compose.yml matches what you're using

**Data not showing in Grafana:**
- Adjust the time range to include your historical data
- Historical data might be 1-2 years old, so set "From: now-2y" in time picker

## Notes

- Import is idempotent - running it multiple times won't create duplicates (InfluxDB uses timestamp as unique key)
- Large imports (20,000+ records) may take a few minutes
- The script converts bytes/sec to Mbps automatically
- All your metadata (ISP, server names, IPs) will be preserved
