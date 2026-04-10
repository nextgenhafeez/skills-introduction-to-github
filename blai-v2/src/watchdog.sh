#!/bin/bash
# BLAI Watchdog — monitors health file, restarts if bot is stuck
HEALTH_FILE="/home/tonny/blai-v2/.health"
MAX_STALE_SECONDS=120  # restart if no heartbeat for 2 minutes

while true; do
  sleep 60

  if [ ! -f "$HEALTH_FILE" ]; then
    echo "[WATCHDOG] No health file found, restarting BLAI..."
    pm2 restart blai
    sleep 30
    continue
  fi

  LAST_MODIFIED=$(stat -c %Y "$HEALTH_FILE" 2>/dev/null || echo 0)
  NOW=$(date +%s)
  DIFF=$((NOW - LAST_MODIFIED))

  if [ "$DIFF" -gt "$MAX_STALE_SECONDS" ]; then
    echo "[WATCHDOG] Health stale for ${DIFF}s (>${MAX_STALE_SECONDS}s), restarting BLAI..."
    pm2 restart blai
    sleep 30
  fi
done
