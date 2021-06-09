#!/bin/bash
#Check command
commandlist=("speedtest-cli" "wget" "curl")
for i in "${commandlist[@]}"; do
    if ! [ -x "$(command -v $i)" ]; then
        echo "$i not exist" 
        exit 1
    fi
    done


#Check Internet
wget -q --spider http://google.com
if [ $? -eq 0 ]; then
    echo "Online"
    else
        echo "Offline"
fi

date=$(date +"%Y%m%d_%H%M")
ispheader="ISP"
header1=$(speedtest-cli --csv-header)
isp=$(curl -s ipinfo.io/org)
echo $ispheader,$header1 > test.csv
result=$(speedtest-cli --share --csv)
echo \"$isp\",$result >> test.csv

