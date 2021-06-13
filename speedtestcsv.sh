#!/bin/bash
# Test your internet speed and output to CSV file, intended to run on cron. Using Speedtest from ookla. Speedtest-cli from Sivel will not work and unsupported.   
# Crontab entry example (run every hour): */60 * * * * /home/pi/speedtestcsv/speedtestcsv/speedtestcsv.sh
# Author: Alif Amzari Mohd Azamee
# License MIT


#Speedtest bin path
speedtest="/home/pi/speedtestookla/speedtest"  #PLEASE CHANGE THIS PATH POINT TO WHERE YOU UNTAR YOUR SPEEDTEST INSTALL. For debian/ubuntu, if you install using curl script from official site, just change this path to the absolute path ie /usr/bin/speedtest 
#Get current directory where script is located. Speedtest result.csv will be stored on same directory as script file. 
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
timestamp=$(date --iso-8601=s)
#CSV file header
header1="Server_name,Server_id,Latency,Jitter,Packet_loss,Download,Upload,Download_bytes,Upload_bytes,Share_url"

# Check command
commandlist=("$speedtest" "wget" "curl")
for i in "${commandlist[@]}"; do
    if ! [ -x "$(command -v $i)" ]; then
        echo "$i not exist" 
        exit 1
    fi
done

function header () {
    echo "Time","ISP",$header1,"IP" > $SCRIPT_DIR/result.csv
}
#Check CSV file if exist, and write CSV file if not exist.
if ! [ -f $SCRIPT_DIR/result.csv ]; then
    header
fi

#TODO - Keep only 1 month CSV row (Untested)
mtd=$(date --iso-8601 |cut -d '-' -f2) 
resultlength=$(cat $SCRIPT_DIR/result.csv |wc -l)
csvmnt=$(sed -n '2p' $SCRIPT_DIR/result.csv |cut -d- -f2)
if [ $resultlength > 2 ] && [ $mtd -ne $csvmnt ]; then
    rm $SCRIPT_DIR/result.csv
    sleep 1
    header
fi

#Check internet if offline or online
wget -q --spider http://google.com
internet=$(echo $?)
if [ $internet != 0 ]; then
    #Output offline result to CSV file
    echo "$timestamp","OFFLINE","OFFLINE","OFFLINE","OFFLINE","OFFLINE","OFFLINE","OFFLINE","OFFLINE","OFFLINE","OFFLINE","OFFLINE" >> $SCRIPT_DIR/result.csv
    else 
        #Output online result to CSV file
        isp=$(curl -s ipinfo.io/org)
        ip=$(curl -s /dev/null ifconfig.co 2>&1)
        result=$($speedtest -f csv)
        echo "$timestamp",\"$isp\",$result,"$ip" >> $SCRIPT_DIR/result.csv
fi 