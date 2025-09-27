#!/bin/bash

# Un script care scrie la un anumit interval de timp într-un fișier system-state.log informații legate de sistem
INTERVAL=${INTERVAL:-5}
LOG_FILE="system-state.log"

while true; do
  {
    echo "====================================================="
    echo "================ SYSTEM STATE REPORT ================"
    echo "====================================================="
    echo "Timestamp         : $(date)"
    echo "Hostname          : $(hostname)"
    echo "Uptime            : $(uptime -p)"
    echo "CPU Load Average  : $(uptime | awk -F'load average:' '{ print $2 }' | xargs)"
    echo "Memory Usage      :"
    free -h | awk '$1 == "Mem:" || $1 == "Swap:" {  gsub(":", "", $1); printf "  %s: %s used / %s total\n", $1, $3, $2}'
    echo "Disk Usage (/)    : $(df -h / | awk 'NR==2 {print $3 " used / " $2 " total (" $5 " used)"}')"
    echo "Active Processes  : $(ps aux --no-heading | wc -l)"
    echo "Logged-in Users   : $(who | wc -l)"
    echo "Network (IP addr) : $(hostname -I | awk '{print $1}')"
    echo "====================================================="
  } > "$LOG_FILE"

  sleep "$INTERVAL"
done
