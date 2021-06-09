#!/bin/bash
#Check command
commandlist=("speedtest-cli" "wget" "curl")
for i in "${commandlist[@]}"; do
    if ! [ -x "$(command -v $i)" ]; then
        echo "$i not exist" 
        exit 1
    fi
    done




date=$(date +"%Y%m%d_%H%M")
header1=$(speedtest-cli --csv-header)
result=$(speedtest-cli --share --csv)
isp=$(curl -s ipinfo.io/org)

#Check CSV file if exist, and write CSV file if not exist.
if ! [ -f result.csv ]; then
    echo "ISP",$header1 > result.csv
    #Check internet
    wget -q --spider http://google.com
    if ! [ $? -eq 0 ]; then
    echo "OFFLINE","OFFLINE","OFFLINE","OFFLINE","OFFLINE","OFFLINE","OFFLINE","OFFLINE","OFFLINE","OFFLINE","OFFLINE" >> result.csv
        else
        echo \"$isp\",$result >> result.csv
    
    fi

fi


