#!/usr/bin/env python3
"""
Internet Speed Test to InfluxDB
Runs Ookla Speedtest CLI and stores results in InfluxDB for Grafana visualization
Author: Alif Amzari Mohd Azamee
License: MIT
"""

import os
import sys
import json
import subprocess
import time
from datetime import datetime
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS

# Environment variables
INFLUXDB_URL = os.getenv('INFLUXDB_URL', 'http://localhost:8086')
INFLUXDB_TOKEN = os.getenv('INFLUXDB_TOKEN', 'my-super-secret-auth-token')
INFLUXDB_ORG = os.getenv('INFLUXDB_ORG', 'speedtest')
INFLUXDB_BUCKET = os.getenv('INFLUXDB_BUCKET', 'speedtest')
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
    """Write speedtest data to InfluxDB"""
    write_api = client.write_api(write_options=SYNCHRONOUS)
    
    point = Point("speedtest")
    
    if is_offline:
        # Write offline status
        point.tag("status", "offline") \
             .field("download", 0.0) \
             .field("upload", 0.0) \
             .field("latency", 0.0) \
             .field("jitter", 0.0) \
             .field("packet_loss", 0.0)
    else:
        # Extract data from speedtest result
        point.tag("status", "online")
        point.tag("isp", data.get('isp', 'Unknown'))
        point.tag("server_name", data.get('server', {}).get('name', 'Unknown'))
        point.tag("server_id", str(data.get('server', {}).get('id', 0)))
        point.tag("server_location", data.get('server', {}).get('location', 'Unknown'))
        point.tag("server_country", data.get('server', {}).get('country', 'Unknown'))
        
        # Convert bits per second to megabits per second
        download_mbps = data.get('download', {}).get('bandwidth', 0) * 8 / 1_000_000
        upload_mbps = data.get('upload', {}).get('bandwidth', 0) * 8 / 1_000_000
        
        point.field("download", round(download_mbps, 2))
        point.field("upload", round(upload_mbps, 2))
        point.field("latency", data.get('ping', {}).get('latency', 0.0))
        point.field("jitter", data.get('ping', {}).get('jitter', 0.0))
        point.field("packet_loss", data.get('packetLoss', 0.0))
        point.field("download_bytes", data.get('download', {}).get('bytes', 0))
        point.field("upload_bytes", data.get('upload', {}).get('bytes', 0))
        
        # Additional metadata
        if 'interface' in data:
            point.tag("interface_name", data['interface'].get('name', 'Unknown'))
            point.field("internal_ip", data['interface'].get('internalIp', ''))
            point.field("external_ip", data['interface'].get('externalIp', ''))
        
        if 'result' in data:
            point.field("result_url", data['result'].get('url', ''))
    
    try:
        write_api.write(bucket=INFLUXDB_BUCKET, record=point)
        print(f"? Data written to InfluxDB at {datetime.now().isoformat()}")
    except Exception as e:
        print(f"? Failed to write to InfluxDB: {e}")

def main():
    """Main loop - run speedtest at specified intervals"""
    print("=== Speedtest to InfluxDB Service ===")
    print(f"InfluxDB URL: {INFLUXDB_URL}")
    print(f"Organization: {INFLUXDB_ORG}")
    print(f"Bucket: {INFLUXDB_BUCKET}")
    print(f"Interval: {SPEEDTEST_INTERVAL} seconds ({SPEEDTEST_INTERVAL/60:.0f} minutes)")
    print("=====================================\n")
    
    # Initialize InfluxDB client
    client = InfluxDBClient(url=INFLUXDB_URL, token=INFLUXDB_TOKEN, org=INFLUXDB_ORG)
    
    # Verify connection
    try:
        health = client.health()
        print(f"? InfluxDB connection: {health.status}")
    except Exception as e:
        print(f"? Failed to connect to InfluxDB: {e}")
        sys.exit(1)
    
    print("\nStarting speedtest monitoring...\n")
    
    while True:
        try:
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
            
            print(f"Next test in {SPEEDTEST_INTERVAL} seconds...\n")
            time.sleep(SPEEDTEST_INTERVAL)
            
        except KeyboardInterrupt:
            print("\n\nShutting down gracefully...")
            client.close()
            sys.exit(0)
        except Exception as e:
            print(f"? Unexpected error: {e}")
            time.sleep(60)  # Wait a minute before retrying

if __name__ == "__main__":
    main()
