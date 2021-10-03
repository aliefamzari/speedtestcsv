
<# Test your internet speed and output to CSV file.
Intended to run on scheduler task.
Script will download,unzip speedtest binary and save it to C:\ProgramData\SpeedtestCLI\
Result will be save on C:\ProgramData\SpeedtestCLI\result.csv
Author: Alif Amzari Mohd Azamee
License MIT
#>

# Notification Function
function Show-Notification {
    [cmdletbinding()]
    Param (
        [string]
        $ToastTitle,
        [string]
        [parameter(ValueFromPipeline)]
        $ToastText
    )

    [Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] > $null
    $Template = [Windows.UI.Notifications.ToastNotificationManager]::GetTemplateContent([Windows.UI.Notifications.ToastTemplateType]::ToastText02)

    $RawXml = [xml] $Template.GetXml()
    ($RawXml.toast.visual.binding.text|Where-Object {$_.id -eq "1"}).AppendChild($RawXml.CreateTextNode($ToastTitle)) > $null
    ($RawXml.toast.visual.binding.text|Where-Object {$_.id -eq "2"}).AppendChild($RawXml.CreateTextNode($ToastText)) > $null

    $SerializedXml = New-Object Windows.Data.Xml.Dom.XmlDocument
    $SerializedXml.LoadXml($RawXml.OuterXml)

    $Toast = [Windows.UI.Notifications.ToastNotification]::new($SerializedXml)
    $Toast.Tag = "Powershell"
    $Toast.Group = "PowerShell"
    $Toast.ExpirationTime = [DateTimeOffset]::Now.AddMinutes(1)

    $Notifier = [Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier("PowerShell")
    $Notifier.Show($Toast);
}
Show-Notification SpeedTestCli Running

#Download Ookla speedtest from internet, save to programdata, unzip the zip file.
$DownloadURL = "https://install.speedtest.net/app/cli/ookla-speedtest-1.0.0-win64.zip"
$OutDir = "$($env:ProgramData)\SpeedtestCLI"
try {
    $TestDoownloadLocation =  Test-Path $OutDir
    if (!$TestDoownloadLocation) {
        New-Item $OutDir -ItemType Directory -Force
        Invoke-WebRequest -Uri $DownloadURL -OutFile "$($OutDir)\speedtest.zip"
        Expand-Archive "$($OutDir)\speedtest.zip" -DestinationPath $OutDir -Force
    }
}
catch {
    write-host "Download/extract of speedtestcli failed. Error: $($_.Exception.Message)"
    exit 
}

# Some var
$csvheader = "Time,ISP,Server_name,Server_id,Latency,Jitter,Packet_loss,Download,Upload,Download_bytes,Upload_bytes,Share_url,IP"
$timestamp = Get-Date -UFormat "%Y-%m-%dT%H:%M:%S%Z:00"

# header function
function write-header {
    $csvheader | Out-File $OutDir\result.csv
    
}
#test result.csv if exist or not
$TestFile = Test-Path $OutDir\result.csv
if (!$TestFile) {
    write-header
}

<# TODO Keeep only 1 month CSV row
 $mtd = Get-Date -UFormat %m
 $ytd = Get-Date -UFormat %y
 $resultlength = (Get-Content $OutDir\result.csv).Length
 $csvmnt = (Get-Content $OutDir\result.csv)[1]
 $csvmnt = $csvmnt.Substring(0, $csvmnt.IndexOf(',')) -split ('-') |Select-Object -Index 1
#>

#Check Internet if offline or online
$internet = Test-Connection google.com -Count 2 -quiet
if (!$internet){
    Write-Output "$timestamp,OFFLINE,OFFLINE,OFFLINE,OFFLINE,OFFLINE,OFFLINE,OFFLINE,OFFLINE,OFFLINE,OFFLINE,OFFLINE,OFFLINE" | Add-Content -Path $OutDir\result.csv
    exit 1
}

#Additional data 
$isp = (Invoke-WebRequest -uri "ipinfo.io/org" -UseBasicParsing).content
$ip = (Resolve-DnsName myip.opendns.com -server resolver1.opendns.com -type A).IPaddress

#Perform speedtest
$result = & "$($OutDir)\speedtest.exe" --format=csv --accept-license --accept-gdpr

#trim result to remove line breaks
$trim = Write-Output "$timestamp,$isp,$result,$ip" |out-string
$trim = $trim -replace "`t|`n|`r",""

#Append data to result.csv
$trim | Add-Content -Path $OutDir\result.csv

#Show result to windows notification
$ds = $result -split ',' |Select-Object -Index 5
$ds = $ds.Trim('"')
$ds = [math]::Round($ds / 1000000 * 8, 2)
$us = $result -split ',' |Select-Object -Index 6
$us = $us.Trim('"')
$us = [math]::Round($us / 1000000 * 8, 2)
Show-Notification "SpeedTest Result" "DownloadSpeed=$ds`Mbps UploadSpeed=$us`Mbps" 
