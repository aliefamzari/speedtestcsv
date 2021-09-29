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