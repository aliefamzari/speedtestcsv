#!/usr/bin/env python3
"""
Import historical CSV speedtest data into InfluxDB
Converts CSV format to InfluxDB points with proper unit conversion
"""

import csv
import sys
from datetime import datetime
from influxdb import InfluxDBClient
import os
import glob

# InfluxDB configuration
INFLUXDB_HOST = os.getenv('INFLUXDB_HOST', 'localhost')
INFLUXDB_PORT = int(os.getenv('INFLUXDB_PORT', '8086'))
INFLUXDB_USER = os.getenv('INFLUXDB_USER', 'admin')
INFLUXDB_PASS = os.getenv('INFLUXDB_PASS', 'adminpassword123')
INFLUXDB_DB = os.getenv('INFLUXDB_DB', 'speedtest')

def bytes_per_sec_to_mbps(bytes_per_sec):
    """Convert bytes/sec to Mbps (megabits per second)"""
    if not bytes_per_sec or bytes_per_sec == 'N/A':
        return 0.0
    return float(bytes_per_sec) * 8 / 1_000_000

def parse_csv_row(row):
    """Convert CSV row to InfluxDB point format"""
    try:
        # Parse timestamp
        timestamp = datetime.fromisoformat(row['Time'].replace('+08:00', ''))
        
        # Convert download/upload from bytes/sec to Mbps
        download_mbps = bytes_per_sec_to_mbps(row['Download'])
        upload_mbps = bytes_per_sec_to_mbps(row['Upload'])
        
        # Parse latency and jitter
        latency = float(row['Latency']) if row['Latency'] != 'N/A' else 0.0
        jitter = float(row['Jitter']) if row['Jitter'] != 'N/A' else 0.0
        
        # Parse packet loss
        packet_loss = 0.0
        if row['Packet_loss'] and row['Packet_loss'] != 'N/A':
            packet_loss = float(row['Packet_loss'])
        
        # Create InfluxDB point
        point = {
            "measurement": "speedtest",
            "time": timestamp.isoformat(),
            "fields": {
                "download": round(download_mbps, 2),
                "upload": round(upload_mbps, 2),
                "latency": round(latency, 3),
                "jitter": round(jitter, 3),
                "packet_loss": packet_loss,
                "download_bytes": int(row['Download_bytes']) if row['Download_bytes'] else 0,
                "upload_bytes": int(row['Upload_bytes']) if row['Upload_bytes'] else 0,
            },
            "tags": {
                "isp": row['ISP'].strip('"'),
                "server_name": row['Server_name'].strip('"'),
                "server_id": row['Server_id'].strip('"'),
                "server_location": row['Server_name'].split(' - ')[-1].strip('"') if ' - ' in row['Server_name'] else "Unknown",
                "server_country": "Malaysia",  # Based on your data
                "external_ip": row['IP'],
                "result_url": row['Share_url'],
                "status": "online"
            }
        }
        
        return point
    except Exception as e:
        print(f"Error parsing row: {e}")
        print(f"Row data: {row}")
        return None

def import_csv_file(client, csv_file):
    """Import a single CSV file into InfluxDB"""
    points = []
    
    print(f"\nProcessing: {csv_file}")
    
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            point = parse_csv_row(row)
            if point:
                points.append(point)
    
    if points:
        print(f"  Found {len(points)} records")
        print(f"  Date range: {points[0]['time']} to {points[-1]['time']}")
        
        # Write in batches of 1000
        batch_size = 1000
        for i in range(0, len(points), batch_size):
            batch = points[i:i+batch_size]
            try:
                client.write_points(batch)
                print(f"  Wrote batch {i//batch_size + 1}/{(len(points)-1)//batch_size + 1}")
            except Exception as e:
                print(f"  Error writing batch: {e}")
                return False
        
        print(f"  ? Successfully imported {len(points)} records")
        return True
    else:
        print(f"  No valid records found")
        return False

def main():
    if len(sys.argv) < 2:
        print("Usage: python import_csv_to_influx.py <csv_file_or_directory>")
        print("Example: python import_csv_to_influx.py /path/to/speedtestcsv/*.csv")
        sys.exit(1)
    
    path_pattern = sys.argv[1]
    
    # Connect to InfluxDB
    print(f"Connecting to InfluxDB at {INFLUXDB_HOST}:{INFLUXDB_PORT}")
    client = InfluxDBClient(
        host=INFLUXDB_HOST,
        port=INFLUXDB_PORT,
        username=INFLUXDB_USER,
        password=INFLUXDB_PASS,
        database=INFLUXDB_DB
    )
    
    # Test connection
    try:
        client.ping()
        print("? Connected to InfluxDB")
    except Exception as e:
        print(f"? Failed to connect to InfluxDB: {e}")
        sys.exit(1)
    
    # Get list of CSV files
    csv_files = glob.glob(path_pattern)
    if not csv_files:
        # Try as a directory
        if os.path.isdir(path_pattern):
            csv_files = glob.glob(os.path.join(path_pattern, "*.csv"))
    
    if not csv_files:
        print(f"No CSV files found matching: {path_pattern}")
        sys.exit(1)
    
    # Sort files by name (chronological order)
    csv_files.sort()
    
    print(f"\nFound {len(csv_files)} CSV files to import")
    print("="*60)
    
    # Import each file
    success_count = 0
    for csv_file in csv_files:
        if import_csv_file(client, csv_file):
            success_count += 1
    
    print("\n" + "="*60)
    print(f"Import complete: {success_count}/{len(csv_files)} files imported successfully")
    
    # Show summary
    result = client.query('SELECT COUNT(download) FROM speedtest')
    total_points = list(result.get_points())[0]['count']
    print(f"Total records in database: {total_points}")

if __name__ == "__main__":
    main()
