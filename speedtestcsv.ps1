$DownloadURL = "https://install.speedtest.net/app/cli/ookla-speedtest-1.0.0-win64.zip"
$ScriptDir = "$($env:ProgramData)\SpeedtestCLI"
try {
    $TestDoownloadLocation =  Test-Path $ScriptDir
    if (!$TestDoownloadLocation) {
        New-Item $ScriptDir -ItemType Directory -Force
        Invoke-WebRequest -Uri $DownloadURL -OutFile "$($ScriptDir)\speedtest.zip"
        Expand-Archive "$($ScriptDir)\speedtest.zip" -DestinationPath $ScriptDir -Force
    }
}
catch {
    write-host "Download/extract of speedtestcli failed. Error: $($_.Exception.Message)"
    exit 
}
$csvheader = "Time,ISP,Server_name,Server_id,Latency,Jitter,Packet_loss,Download,Upload,Download_bytes,Upload_bytes,Share_url,IP"
$timestamp = get-date -UFormat "%Y-%m-%dT%H:%M:%S%Z:00"

function write-header {
    $csvheader | Out-File $ScriptDir\result.csv
    
}

$TestFile = Test-Path $ScriptDir\result.csv
if (!$TestFile) {
    write-header
}

#Check Internet if offline or online
#$internet = Invoke-WebRequest -uri "http://google.com" -UseBasicParsing
$internet = Test-Connection google.com -Count 2 -quiet
if (!$internet){
    Write-Output "$timestamp,OFFLINE,OFFLINE,OFFLINE,OFFLINE,OFFLINE,OFFLINE,OFFLINE,OFFLINE,OFFLINE,OFFLINE,OFFLINE,OFFLINE" | Add-Content -Path $ScriptDir\result.csv
    exit 1
}

$isp = (Invoke-WebRequest -uri "ipinfo.io/org" -UseBasicParsing).content
$ip = (Resolve-DnsName myip.opendns.com -server resolver1.opendns.com -type A).IPaddress
$result = & "$($scriptdir)\speedtest.exe" --format=csv --accept-license --accept-gdpr

#"$timestamp, $isp,$result,$ip" | Add-Content -Path $ScriptDir\result.csv
$trim = Write-Output "$timestamp,$isp,$result,$ip" |out-string
$trim = $trim -replace "`t|`n|`r",""
$trim | Add-Content -Path $ScriptDir\result.csv

