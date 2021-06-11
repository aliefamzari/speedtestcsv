#!/bin/bash
#Check command
commandlist=("/home/pi/speedtestookla/speedtest" "wget" "curl")
for i in "${commandlist[@]}"; do
    if ! [ -x "$(command -v $i)" ]; then
        echo "$i not exist" 
        exit 1
    fi
    done


#Todo
#define PATH

timestamp=$(date --iso-8601=s)
header1="Server_name,Server_id,Latency,Jitter,Packet_loss,Download,Upload,Download_bytes,Upload_bytes,Share_url"
#Check CSV file if exist, and write CSV file if not exist.
if ! [ -f result.csv ]; then
    echo "Time", "ISP",$header1 > result.csv
fi

#Check internet
wget -q --spider http://google.com
internet=$(echo $?)
if [ $internet != 0 ]; then
    echo "$timestamp","OFFLINE","OFFLINE","OFFLINE","OFFLINE","OFFLINE","OFFLINE","OFFLINE","OFFLINE","OFFLINE","OFFLINE" >> result.csv
    else 
        isp=$(curl -s ipinfo.io/org)
        result=$(/home/pi/speedtestookla/speedtest -f csv)
        echo "$timestamp",\"$isp\",$result >> result.csv
fi  
        




