# speedtestcsv

**Linux/Bash (speedtestcsv.sh)**

**Requirement:** Speedtest bin from https://www.speedtest.net/apps/cli. Please manually download the bin from official site. 

1. Test your internet speed and output to CSV file, intended to run on cron. Using Speedtest from ookla. Speedtest-cli from Sivel will not work and unsupported. 
2. For debian/ubuntu, if you install using curl script from official site, change the bin path variable to absolute path ie /usr/bin/speedtest    
3. Crontab entry example (run every hour): */60 * * * * /home/pi/speedtestcsv/speedtestcsv.sh

**Windows/Powershell (speedtestcsv.ps1)**

1. Test your internet speed and output to CSV file.
2. Powershell script will download,unzip speedtest binary and save it to C:\ProgramData\SpeedtestCLI\
3. Result will be save on C:\ProgramData\SpeedtestCLI\result.csv
4. Intended to run as task scheduler. For example every 1 hour. 
5. Download/Upload result will popup as windows notification on each run. 


Output sample:
![Sample result](https://github.com/aliefamzari/speedtestcsv/blob/main/img/soffice.bin_qio75nrrsIa.png?raw=true "Optional Title")
