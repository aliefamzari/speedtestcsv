# speedtestcsv
Test your internet speed and output to CSV file, intended to run on cron. Using Speedtest from ookla. Speedtest-cli from Sivel will not work and unsupported. For debian/ubuntu, if you install using curl script from official site, just change this path to the absolute path ie /usr/bin/speedtest    
Crontab entry example (run every hour): */60 * * * * /home/pi/speedtestcsv/speedtestcsv/speedtestcsv.sh


Output sample:
![Sample result](https://github.com/aliefamzari/speedtestcsv/blob/main/img/excelspeedtest.PNG?raw=true "Optional Title")
