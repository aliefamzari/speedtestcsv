#!/usr/bin/env python3
"""
Internet Speed Test to InfluxDB v1.8
Runs Ookla Speedtest CLI and stores results in InfluxDB for Grafana visualization
Compatible with Raspberry Pi ARM architecture
Author: Alif Amzari Mohd Azamee
License: MIT
"""

import os
import sys
import json
import subprocess
import time
from datetime import datetime, timedelta
from influxdb import InfluxDBClient

# Environment variables
INFLUXDB_HOST = os.getenv('INFLUXDB_HOST', 'influxdb')
INFLUXDB_PORT = int(os.getenv('INFLUXDB_PORT', '8086'))
INFLUXDB_USER = os.getenv('INFLUXDB_USER', 'admin')
INFLUXDB_PASSWORD = os.getenv('INFLUXDB_PASSWORD', 'adminpassword123')
INFLUXDB_DATABASE = os.getenv('INFLUXDB_DATABASE', 'speedtest')
SPEEDTEST_INTERVAL = int(os.getenv('SPEEDTEST_INTERVAL', '3600'))  # Default: 1 hour

def check_internet():
    """Check if internet is available"""
    try:
        subprocess.run(['ping', '-c', '1', 'google.com'], 
                      stdout=subprocess.DEVNULL, 
                      stderr=subprocess.DEVNULL, 
                      timeout=5, 
                      check=True)
        return True
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
        return False

def run_speedtest():
    """Run Ookla Speedtest and return results"""
    try:
        result = subprocess.run(
            ['speedtest', '--accept-license', '--accept-gdpr', '-f', 'json'],
            capture_output=True,
            text=True,
            timeout=60,
            check=True
        )
        return json.loads(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Speedtest failed: {e}")
        return None
    except subprocess.TimeoutExpired:
        print("Speedtest timed out")
        return None
    except json.JSONDecodeError as e:
        print(f"Failed to parse speedtest output: {e}")
        return None

def write_to_influxdb(client, data, is_offline=False):
    """Write speedtest data to InfluxDB v1.8"""
    
    json_body = []
    
    if is_offline:
        # Write offline status
        point = {
            "measurement": "speedtest",
            "tags": {
                "status": "offline"
            },
            "fields": {
                "download": 0.0,
                "upload": 0.0,
                "latency": 0.0,
                "jitter": 0.0,
                "packet_loss": 0.0
            }
        }
    else:
        # Extract data from speedtest result
        # Convert bits per second to megabits per second
        download_mbps = data.get('download', {}).get('bandwidth', 0) * 8 / 1_000_000
        upload_mbps = data.get('upload', {}).get('bandwidth', 0) * 8 / 1_000_000
        
        point = {
            "measurement": "speedtest",
            "tags": {
                "status": "online",
                "isp": data.get('isp', 'Unknown'),
                "server_name": data.get('server', {}).get('name', 'Unknown'),
                "server_id": str(data.get('server', {}).get('id', 0)),
                "server_location": data.get('server', {}).get('location', 'Unknown'),
                "server_country": data.get('server', {}).get('country', 'Unknown')
            },
            "fields": {
                "download": round(download_mbps, 2),
                "upload": round(upload_mbps, 2),
                "latency": data.get('ping', {}).get('latency', 0.0),
                "jitter": data.get('ping', {}).get('jitter', 0.0),
                "packet_loss": data.get('packetLoss', 0.0),
                "download_bytes": data.get('download', {}).get('bytes', 0),
                "upload_bytes": data.get('upload', {}).get('bytes', 0)
            }
        }
        
        # Additional metadata
        if 'interface' in data:
            point['tags']['interface_name'] = data['interface'].get('name', 'Unknown')
            point['fields']['internal_ip'] = data['interface'].get('internalIp', '')
            point['fields']['external_ip'] = data['interface'].get('externalIp', '')
        
        if 'result' in data:
            point['fields']['result_url'] = data['result'].get('url', '')
    
    json_body.append(point)
    
    try:
        client.write_points(json_body)
        print(f"? Data written to InfluxDB at {datetime.now().isoformat()}")
    except Exception as e:
        print(f"? Failed to write to InfluxDB: {e}")

def wait_until_next_hour():
    """Calculate seconds until the next full hour"""
    now = datetime.now()
    next_hour = now.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)
    seconds_until_next_hour = (next_hour - now).total_seconds()
    return seconds_until_next_hour

def main():
    """Main loop - run speedtest at the top of every hour"""
    print("=== Speedtest to InfluxDB Service ===")
    print(f"InfluxDB Host: {INFLUXDB_HOST}:{INFLUXDB_PORT}")
    print(f"Database: {INFLUXDB_DATABASE}")
    print(f"Schedule: Every hour at :00 (e.g., 1:00, 2:00, 3:00, etc.)")
    print("=====================================\n")
    
    # Initialize InfluxDB client
    client = InfluxDBClient(
        host=INFLUXDB_HOST,
        port=INFLUXDB_PORT,
        username=INFLUXDB_USER,
        password=INFLUXDB_PASSWORD,
        database=INFLUXDB_DATABASE
    )
    
    # Verify connection and create database if it doesn't exist
    try:
        client.ping()
        print(f"? InfluxDB connection successful")
        
        # Create database if it doesn't exist
        databases = client.get_list_database()
        if not any(db['name'] == INFLUXDB_DATABASE for db in databases):
            client.create_database(INFLUXDB_DATABASE)
            print(f"? Created database: {INFLUXDB_DATABASE}")
        else:
            print(f"? Database exists: {INFLUXDB_DATABASE}")
            
    except Exception as e:
        print(f"? Failed to connect to InfluxDB: {e}")
        sys.exit(1)
    
    print("\nStarting speedtest monitoring...\n")
    
    # Run first test immediately
    first_run = True
    
    while True:
        try:
            if first_run:
                print("Running initial speedtest...")
                first_run = False
            else:
                # Wait until the next full hour
                wait_time = wait_until_next_hour()
                next_run = datetime.now() + timedelta(seconds=wait_time)
                print(f"Next test at: {next_run.strftime('%Y-%m-%d %H:%M:%S')} (in {wait_time/60:.1f} minutes)\n")
                time.sleep(wait_time)
            
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Running speedtest...")
            
            # Check internet connectivity
            if not check_internet():
                print("? Internet is offline")
                write_to_influxdb(client, None, is_offline=True)
            else:
                # Run speedtest
                result = run_speedtest()
                
                if result:
                    download = result.get('download', {}).get('bandwidth', 0) * 8 / 1_000_000
                    upload = result.get('upload', {}).get('bandwidth', 0) * 8 / 1_000_000
                    latency = result.get('ping', {}).get('latency', 0)
                    
                    print(f"? Download: {download:.2f} Mbps | Upload: {upload:.2f} Mbps | Latency: {latency:.2f} ms")
                    write_to_influxdb(client, result, is_offline=False)
                else:
                    print("? Speedtest failed")
                    write_to_influxdb(client, None, is_offline=True)
            
        except KeyboardInterrupt:
            print("\n\nShutting down gracefully...")
            client.close()
            sys.exit(0)
        except Exception as e:
            print(f"? Unexpected error: {e}")
            time.sleep(60)  # Wait a minute before retrying

if __name__ == "__main__":
    main()
