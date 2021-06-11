#!/bin/bash
# Test your internet speed and output to CSV file, intended to run on cron. Using Speedtest from ookla. Speedtest-cli from Sivel will not work and unsupported.   
# Author: Alif Amzari Mohd Azamee
# License MIT
# Check command
commandlist=("/home/pi/speedtestookla/speedtest" "wget" "curl")
for i in "${commandlist[@]}"; do
    if ! [ -x "$(command -v $i)" ]; then
        echo "$i not exist" 
        exit 1
    fi
done

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"


timestamp=$(date --iso-8601=s)
header1="Server_name,Server_id,Latency,Jitter,Packet_loss,Download,Upload,Download_bytes,Upload_bytes,Share_url"
#Check CSV file if exist, and write CSV file if not exist.
if ! [ -f $SCRIPT_DIR/result.csv ]; then
    echo "Time", "ISP",$header1 > $SCRIPT_DIR/result.csv
fi

#Check internet
wget -q --spider http://google.com
internet=$(echo $?)
if [ $internet != 0 ]; then
    echo "$timestamp","OFFLINE","OFFLINE","OFFLINE","OFFLINE","OFFLINE","OFFLINE","OFFLINE","OFFLINE","OFFLINE","OFFLINE" >> $SCRIPT_DIR/result.csv
    else 
        isp=$(curl -s ipinfo.io/org)
        result=$(/home/pi/speedtestookla/speedtest -f csv)
        echo "$timestamp",\"$isp\",$result >> $SCRIPT_DIR/result.csv
fi  
        




