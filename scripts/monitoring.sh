#!/bin/bash
set -euo pipefail

INTERVAL=${INTERVAL:-5}
LOG_FILE="/data/system-state.log"

if ! touch "$LOG_FILE" 2>/dev/null; then
  echo "Eroare: Nu se poate scrie în $LOG_FILE" >&2; exit 1
fi
[[ "$INTERVAL" =~ ^[0-9]+$ ]] && (( INTERVAL > 0 )) || { echo "Eroare: INTERVAL invalid" >&2; exit 1; }

print_section() { printf "%-25s: %s\n" "$1" "$2"; }

while :; do
{
  printf '%s\n' "+---------------------------------------------------------------+"
  printf '%s\n' "|                   SYSTEM STATE REPORT                         |"
  printf '%s\n' "+---------------------------------------------------------------+"
  echo

  print_section "Timestamp"         "$(date '+%a %d %b %Y %H:%M:%S %Z')"
  print_section "Hostname"          "$(hostname)"
  print_section "Uptime"            "$(uptime -p 2>/dev/null || echo 'N/A')"

  load=$(awk '{print $1,$2,$3}' /proc/loadavg 2>/dev/null || echo "N/A")
  print_section "CPU Load (1/5/15)" "$load"

  echo "+-- Memory Usage"
  free -h 2>/dev/null | awk '
    $1~/Mem/  {gsub(/:/,"",$1); printf "|   %-8s: %8s used / %8s total\n", $1, $3, $2}
    $1~/Swap/ {gsub(/:/,"",$1); printf "|   %-8s: %8s used / %8s total\n", $1, $3, $2}
  ' || echo "|   N/A"

  echo
  echo "+-- Disk Usage (/)"
  if disk=$(df -h / 2>/dev/null | awk 'NR==2'); then
    used=$(awk '{print $3}' <<<"$disk")
    total=$(awk '{print $2}' <<<"$disk")
    pct=$(awk '{gsub(/%/,""); print $5}' <<<"$disk")
    printf "|   Used: %8s / %-8s (%3s%% used)\n" "$used" "$total" "$pct"
    (( pct >= 90 )) && echo "|   WARNING: Disk critically high ($pct%)"
  else
    echo "|   N/A"
  fi

  echo
  print_section "Active Processes" "$(ls /proc 2>/dev/null | grep -E '^[0-9]+$' | wc -l || echo N/A)"
  print_section "Logged-in Users"  "$(who 2>/dev/null | wc -l || echo N/A)"
  print_section "Primary IP"       "$(hostname -I 2>/dev/null | awk '{print $1}' || echo N/A)"

  # === NETWORK INTERFACES ===

  echo
  echo "+-- Network Interfaces (RX/TX bytes)"
  out=$(ip -s link 2>/dev/null | awk '
    /^[0-9]+:/ {
      if (iface != "" && rx != "" && tx != "")
        printf "|   %-15s: RX %12s  | TX %12s\n", iface, rx, tx
      iface = substr($2, 1, length($2)-1)
      rx = tx = ""
      next
    }
    /RX:/ { getline; rx = $1; next }
    /TX:/ { getline; tx = $1; next }
    END {
      if (iface != "" && rx != "" && tx != "")
        printf "|   %-15s: RX %12s  | TX %12s\n", iface, rx, tx
    }
  ')
  if [[ -n "$out" ]]; then
    echo "$out"
  else
    echo "|   N/A"
  fi

  echo
  if command -v sensors >/dev/null 2>&1; then
    temp=$(sensors 2>/dev/null | awk '/Core 0/ {print $3; exit}' || echo "N/A")
    print_section "CPU Temperature" "${temp:-N/A}"
  else
    print_section "CPU Temperature" "N/A (sensors not installed)"
  fi

  echo
  echo "+-- Top 5 CPU Processes"
  ps aux --sort=-%cpu 2>/dev/null | head -n 6 | tail -n 5 | awk '
    {
      cmd = $11; for(i=12;i<=NF;i++) cmd = cmd " " $i
      if (length(cmd) > 60) cmd = substr(cmd,1,57) "..."
      printf "|   PID: %6s  CPU: %5s%%  MEM: %5s%%  CMD: %s\n", $2, $3, $4, cmd
    }
  ' || echo "|   N/A"

  echo
  if command -v docker >/dev/null 2>&1; then
    running=$(docker ps -q 2>/dev/null | wc -l || echo 0)
    echo "+-- Docker Containers"
    print_section "  Running" "$running"
    echo "+-- Top Containers (by name)"
    docker ps --format '{{.ID}}\t{{.Names}}\t{{.Status}}' 2>/dev/null |
      head -n 3 | awk '{printf "    → %s  %-20s %s\n", $1, $2, $3}' ||
      echo "    N/A"
  else
    echo "+-- Docker Containers"
    print_section "  Status" "N/A (docker not installed)"
  fi

  # === KUBERNETES PODS ===
  echo
  if command -v kubectl >/dev/null 2>&1; then
    echo "+-- Kubernetes Pods"
    pods_output=$(kubectl get pods --no-headers 2>/dev/null)
    if [[ -n "$pods_output" ]]; then
      running=$(awk '$3=="Running"{c++} END{print c+0}' <<<"$pods_output")
      failed=$(awk '$3!="Running"{c++} END{print c+0}' <<<"$pods_output")
      printf "|  %-12s %s\n" "Running:" "$running"
      printf "|  %-12s %s\n" "Failed:"  "$failed"
      echo "+-----------------------"
    else
      print_section "  Status" "No pods found"
    fi
  else
    echo "+-- Kubernetes Pods"
    print_section "  Status" "N/A (kubectl not installed)"
  fi

  echo
  os=$(grep -m1 '^PRETTY_NAME=' /etc/os-release 2>/dev/null | cut -d'"' -f2 || echo "N/A")
  print_section "OS Version" "$os"

  echo
  printf '%s\n' "+---------------------------------------------------------------+"
  echo
} > "$LOG_FILE"

sleep "$INTERVAL"
done