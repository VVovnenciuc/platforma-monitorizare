#!/bin/bash
set -euo pipefail

INTERVAL=${INTERVAL:-5}
DATA_DIR="${DATA_DIR:-/data}"
LOG_FILE="$DATA_DIR/system-state.log"

# Verifică dacă se poate scrie în fișierul de log
if ! touch "$LOG_FILE" 2>/dev/null; then
  echo "Eroare: Nu se poate scrie în $LOG_FILE" >&2
  exit 1
fi

# Validare interval
[[ "$INTERVAL" =~ ^[0-9]+$ ]] && (( INTERVAL > 0 )) || {
  echo "Eroare: INTERVAL invalid ($INTERVAL)" >&2
  exit 1
}

print_section() { printf "%-25s: %s\n" "$1" "$2"; }

while :; do
{
  printf '%s\n' "+---------------------------------------------------------------+"
  printf '%s\n' "|                   SYSTEM STATE REPORT                         |"
  printf '%s\n' "+---------------------------------------------------------------+"
  echo

  # --- Timestamp & Host ---
  print_section "Timestamp" "$(date '+%a %d %b %Y %H:%M:%S %Z')"
  print_section "Hostname" "$(hostname)"
  print_section "Uptime" "$(awk '{print int($1/3600)"h "int(($1%3600)/60)"m"}' /host/proc/uptime 2>/dev/null || echo 'N/A')"

  # --- CPU Load ---
  load=$(awk '{print $1,$2,$3}' /host/proc/loadavg 2>/dev/null || echo "N/A")
  print_section "CPU Load (1/5/15)" "$load"

  # --- Memory Usage ---
  echo "+-- Memory Usage"
  awk '/MemTotal/ {total=$2} /MemAvailable/ {avail=$2} END{
    used=total-avail
    if(used>1024){used_val=used/1024; u="MB"} else {used_val=used; u="kB"}
    if(total>1024){total_val=total/1024; tu="MB"} else {total_val=total; tu="kB"}
    printf "|   Memory: used %6.1f %s / total %6.1f %s\n", used_val, u, total_val, tu
  }' /host/proc/meminfo 2>/dev/null || echo "|   N/A"

  # --- Disk Usage ---
  echo
  echo "+-- Disk Usage (/)"
  if disk=$(df -h "$DATA_DIR" 2>/dev/null | awk 'NR==2'); then
    used=$(awk '{print $3}' <<<"$disk")
    total=$(awk '{print $2}' <<<"$disk")
    pct=$(awk '{gsub(/%/,""); print $5}' <<<"$disk")
    printf "|   Used: %8s / %-8s (%3s%% used)\n" "$used" "$total" "$pct"
    (( pct >= 90 )) && echo "|   WARNING: Disk critically high ($pct%)"
  else
    echo "|   N/A"
  fi

  # --- Processes & Users ---
  echo
  print_section "Active Processes" "$(ls /host/proc 2>/dev/null | grep -E '^[0-9]+$' | wc -l || echo N/A)"
  print_section "Logged-in Users" "$(who 2>/dev/null | wc -l || echo N/A)"
  print_section "Primary IP" "$(hostname -I 2>/dev/null | awk '{print $1}' || echo N/A)"

  # --- Network Interfaces ---
  echo
  echo "+-- Network Interfaces (RX/TX bytes)"
  ip -s link 2>/dev/null | awk '
    /^[0-9]+:/ {if(iface!="" && rx!="" && tx!="") printf "|   %-15s: RX %12s  | TX %12s\n", iface, rx, tx; iface=substr($2,1,length($2)-1); rx=tx=""}
    /RX:/ {getline; rx=$1}
    /TX:/ {getline; tx=$1}
    END {if(iface!="" && rx!="" && tx!="") printf "|   %-15s: RX %12s  | TX %12s\n", iface, rx, tx}'

  # --- Top 5 CPU Processes ---
  echo
  echo "+-- Top 5 CPU Processes"
  ps -eo pid,pcpu,pmem,comm --sort=-pcpu | head -n 6 | tail -n 5 |
    awk '{printf "|   PID: %6s  CPU: %5s%%  MEM: %5s%%  CMD: %s\n", $1, $2, $3, $4}'

  # --- OS Info ---
  echo
  # Detectăm fișierul OS de pe host (etc sau usr/lib)
  HOST_OS_FILE="/host/etc/os-release"
  [ ! -f "$HOST_OS_FILE" ] && HOST_OS_FILE="/host/usr/lib/os-release"
  if [ -f "$HOST_OS_FILE" ]; then
    OS_NAME=$(grep '^NAME=' "$HOST_OS_FILE" | cut -d= -f2 | tr -d '"')
    OS_VERSION=$(grep '^VERSION=' "$HOST_OS_FILE" | cut -d= -f2 | tr -d '"')
    OS_INFO="$OS_NAME $OS_VERSION"
  else
    OS_INFO="N/A"
  fi
  print_section "OS Version" "$OS_INFO"

  echo
  printf '%s\n' "+---------------------------------------------------------------+"
  echo

} > "$LOG_FILE"

sleep "$INTERVAL"
done