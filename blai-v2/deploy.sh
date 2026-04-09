#!/bin/bash
# BLAI v2 — Deploy to Google Cloud VM
# Usage: bash deploy.sh

set -e

VM="blacklayers-agent"
ZONE="us-central1-a"
REMOTE_DIR="/home/tonny/blai-v2"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "=== BLAI v2 Deployment ==="
echo ""

# 1. Stop old OpenClaw
echo "[1/6] Stopping OpenClaw..."
gcloud compute ssh $VM --zone=$ZONE --command="
systemctl --user stop openclaw-gateway.service 2>/dev/null || true
systemctl --user disable openclaw-gateway.service 2>/dev/null || true
# Stop any running BLAI
pm2 stop blai 2>/dev/null || true
pkill -f 'node.*whatsapp.js' 2>/dev/null || true
echo 'Old services stopped'
"

# 2. Upload BLAI v2
echo "[2/6] Uploading BLAI v2..."
gcloud compute ssh $VM --zone=$ZONE --command="mkdir -p $REMOTE_DIR"
gcloud compute scp --recurse "$SCRIPT_DIR/src" "$SCRIPT_DIR/skills" "$SCRIPT_DIR/config" "$SCRIPT_DIR/package.json" $VM:$REMOTE_DIR/ --zone=$ZONE

# 3. Install dependencies
echo "[3/6] Installing dependencies..."
gcloud compute ssh $VM --zone=$ZONE --command="
cd $REMOTE_DIR
npm install --production
pip3 install requests 2>/dev/null || true
mkdir -p memory/conversations memory/daily
echo 'Dependencies installed'
"

# 4. Set up environment
echo "[4/6] Setting up environment..."
gcloud compute ssh $VM --zone=$ZONE --command="
# Set env vars
grep -q 'GOOGLE_API_KEY' ~/.bashrc || echo 'export GOOGLE_API_KEY=AIzaSyAAoPq4MFNKn1VBztRBp2hfWn2dcw_jCQs' >> ~/.bashrc

# Install pm2 for process management
which pm2 > /dev/null 2>&1 || npm install -g pm2
echo 'Environment ready'
"

# 5. Set up cron for scheduled tasks
echo "[5/6] Setting up scheduler..."
gcloud compute ssh $VM --zone=$ZONE --command="
# Remove old OpenClaw crons
crontab -l 2>/dev/null | grep -v openclaw | grep -v blai-safe-start > /tmp/clean_cron || true

# Add BLAI v2 scheduled tasks
cat >> /tmp/clean_cron << 'CRON'
# BLAI v2 Scheduler
0 7 * * * cd /home/tonny/blai-v2 && python3 src/scheduler.py morning >> /tmp/blai-scheduler.log 2>&1
30 7 * * * cd /home/tonny/blai-v2 && python3 src/scheduler.py richbrain >> /tmp/blai-scheduler.log 2>&1
0 9 * * * cd /home/tonny/blai-v2 && python3 src/scheduler.py content >> /tmp/blai-scheduler.log 2>&1
0 10 * * * cd /home/tonny/blai-v2 && python3 src/scheduler.py leads >> /tmp/blai-scheduler.log 2>&1
0 14 * * * cd /home/tonny/blai-v2 && python3 src/scheduler.py email >> /tmp/blai-scheduler.log 2>&1
0 18 * * * cd /home/tonny/blai-v2 && python3 src/scheduler.py evening >> /tmp/blai-scheduler.log 2>&1
0 22 * * * cd /home/tonny/blai-v2 && python3 src/scheduler.py scorecard >> /tmp/blai-scheduler.log 2>&1
0 10 * * 0 cd /home/tonny/blai-v2 && python3 src/scheduler.py weekly >> /tmp/blai-scheduler.log 2>&1
CRON
crontab /tmp/clean_cron
echo 'Cron tasks set'
crontab -l | grep blai
"

# 6. Start BLAI v2
echo "[6/6] Starting BLAI v2..."
gcloud compute ssh $VM --zone=$ZONE --command="
cd $REMOTE_DIR
pm2 start src/whatsapp.js --name blai --restart-delay=5000
pm2 save
pm2 startup 2>/dev/null || true
echo ''
echo '=== BLAI v2 is LIVE ==='
pm2 status
"

echo ""
echo "=== DEPLOYMENT COMPLETE ==="
echo "BLAI v2 is running on the VM."
echo "First time: scan QR code with WhatsApp"
echo "Check logs: gcloud compute ssh $VM --zone=$ZONE --command='pm2 logs blai'"
