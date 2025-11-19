# speedtestcsv

Monitor your internet speed with automated testing and live Grafana dashboards.

## 🚀 Docker Solution (Recommended)

**Automated speedtest monitoring with InfluxDB + Grafana**

- 🐳 Runs in Docker containers (perfect for Raspberry Pi/Portainer)
- 📊 Live Grafana dashboards with historical data visualization
- ⏰ Automatic hourly testing at :00 (e.g., 1:00, 2:00, 3:00...)
- 🔄 InfluxDB 1.8 time-series database
- 📈 Track download/upload speeds, latency, jitter, packet loss

### Quick Start

```bash
git clone https://github.com/aliefamzari/speedtestcsv.git
cd speedtestcsv
docker compose up -d
```

Access Grafana at `http://localhost:3000` (default login: admin/admin)

**Documentation:**
- [📖 Docker Deployment Guide](DOCKER_README.md)
- [🔧 Raspberry Pi Setup](RASPBERRY_PI_README.md)
- [📥 Import Historical CSV Data](IMPORT_HISTORICAL_DATA.md)
- [⚙️ ARM Compatibility Notes](ARM_COMPATIBILITY_NOTES.md)

---

## 📜 Legacy CSV Scripts (Deprecated)

> ⚠️ **Note**: The standalone bash/PowerShell scripts are deprecated in favor of the Docker solution above. They remain available for backward compatibility.

<details>
<summary><b>Linux/Bash (speedtestcsv.sh)</b> - Click to expand</summary>

**Requirement:** Speedtest CLI from https://www.speedtest.net/apps/cli

1. Tests internet speed and outputs to CSV file
2. Intended for cron scheduling
3. For Debian/Ubuntu, use absolute path: `/usr/bin/speedtest`
4. Crontab example (hourly): `0 * * * * /home/pi/speedtestcsv/speedtestcsv.sh`

</details>

<details>
<summary><b>Windows/PowerShell (speedtestcsv.ps1)</b> - Click to expand</summary>

1. Tests internet speed and outputs to CSV file
2. Auto-downloads Speedtest CLI to `C:\ProgramData\SpeedtestCLI\`
3. Results saved to `C:\ProgramData\SpeedtestCLI\result.csv`
4. Intended for Task Scheduler (hourly)
5. Shows Windows notifications with results

![Notification](https://github.com/aliefamzari/speedtestcsv/blob/main/img/cUPV0RibaL.png?raw=true)

</details>

**CSV Output Sample:**
![Sample result](https://github.com/aliefamzari/speedtestcsv/blob/main/img/soffice.bin_qio75nrrsIa.png?raw=true)
