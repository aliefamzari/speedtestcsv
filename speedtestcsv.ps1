$DownloadURL = "https://install.speedtest.net/app/cli/ookla-speedtest-1.0.0-win64.zip"
$DownloadLocation = "$($env:ProgramData)\SpeedtestCLI"
try {
    $TestDoownloadLocation =  Test-Path $DownloadLocation
    if (!$TestDoownloadLocation) {
        New-Item $DownloadLocation -ItemType Directory -Force
        Invoke-WebRequest -Uri $DownloadURL -OutFile "$($DownloadLocation)\speedtest.zip"
        Expand-Archive "$($DownloadLocation)\speedtest.zip" -DestinationPath $DownloadLocation -Force
    }
}
catch {
    write-host "Download/extract of speedtestcli failed. Error: $($_.Exception.Message)"
    exit 
}
$csvheader = "Time,ISP,Server_name,Server_id,Latency,Jitter,Packet_loss,Download,Upload,Download_bytes,Upload_bytes,Share_url,IP"
$timestamp = get-date -UFormat "%Y-%m-%dT%H:%M:%S%Z:00"
