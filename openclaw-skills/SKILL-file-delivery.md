---
name: file-delivery
description: Deliver files from VM to Boss's Mac via SCP/Tailscale — with retry logic, fallback methods, and delivery confirmation
triggers:
  - "send me", "deliver", "transfer", "download"
  - "send the file", "send the video", "send the image"
  - After any content generation that Boss requested
---

# SKILL: File Delivery to Boss's Mac

## Purpose
Deliver any generated file (video, image, PDF, etc.) directly to Boss's Mac Downloads folder via SCP over Tailscale.

## Connection Details
- **Mac Tailscale IP**: `100.105.165.84` (static — never changes)
- **Mac username**: `tonny`
- **Destination**: `/Users/tonny/Downloads/`
- **SSH key**: Already configured at `~/.ssh/id_ed25519`

## How to Deliver a File

### Step 1: Verify the file exists locally
```bash
ls -lh /path/to/file
```

### Step 2: SCP the file to Boss's Mac
```bash
scp -o ConnectTimeout=15 /path/to/file tonny@100.105.165.84:/Users/tonny/Downloads/
```

### Step 3: Verify delivery
```bash
ssh -o ConnectTimeout=15 tonny@100.105.165.84 "ls -lh /Users/tonny/Downloads/$(basename /path/to/file)"
```

### Step 4: Confirm to Boss
Send message: "File delivered to your Downloads folder: **filename.ext** (size)"

## Common File Paths on VM
- Videos: `/home/tonny/content/videos/`
- Images: `/home/tonny/content/images/`
- Generated content: `/home/tonny/content/`

## Rules
- ALWAYS use Tailscale IP `100.105.165.84` — never use local network IP (it changes)
- ALWAYS verify the file exists before sending
- ALWAYS confirm delivery with filename and size
- If SCP fails, check: is Tailscale running? (`tailscale status`) Is Mac awake?
- For large files (>100MB), warn Boss it may take a moment
- NEVER delete the source file after delivery — keep the VM copy as backup

## Troubleshooting
If connection refused:
1. Check Tailscale: `tailscale status` — Mac should show as "active" not "idle"
2. Check SSH: `ssh -v tonny@100.105.165.84` for debug output
3. Mac may be asleep — tell Boss to wake it up

## Example Usage
Boss says: "Send me the latest video"
```bash
scp -o ConnectTimeout=15 /home/tonny/content/videos/latest.mp4 tonny@100.105.165.84:/Users/tonny/Downloads/
ssh -o ConnectTimeout=15 tonny@100.105.165.84 "ls -lh /Users/tonny/Downloads/latest.mp4"
```
Reply: "File delivered to your Downloads: **latest.mp4** (12.3 MB)"

## Fallback Delivery Methods
If SCP over Tailscale fails after 3 retries:

### Fallback 1: Google Cloud Storage (temporary link)
```bash
gsutil cp /path/to/file gs://blacklayers-temp/
gsutil signurl -d 24h ~/.config/gcloud/service-account.json gs://blacklayers-temp/filename
# Send signed URL to Boss via WhatsApp
```

### Fallback 2: Direct HTTP server (temporary)
```bash
cd /home/tonny/content/
python3 -m http.server 9090 --bind 0.0.0.0 &
# Send link: http://34.132.116.116:9090/filename
# Kill server after Boss confirms download
kill %1
```

### Fallback 3: Save for later
```bash
cp /path/to/file ~/content/pending-delivery/
echo "$(date): $filename — awaiting delivery" >> ~/content/pending-delivery/log.txt
# Notify Boss: "File saved, will deliver when Mac is online"
```

## Retry Logic
```bash
MAX_RETRIES=3
RETRY_DELAY=30  # seconds

for i in $(seq 1 $MAX_RETRIES); do
  scp -o ConnectTimeout=15 "$FILE" tonny@100.105.165.84:/Users/tonny/Downloads/ && break
  echo "Attempt $i failed, retrying in ${RETRY_DELAY}s..."
  sleep $RETRY_DELAY
done
```

## Error Handling
| Error | Fix |
|-------|-----|
| Connection refused | Check Tailscale status, try fallback methods |
| Permission denied | Check SSH key: `ssh-add ~/.ssh/id_ed25519` |
| Disk full on Mac | Warn Boss, suggest cleanup, use GCS fallback |
| File too large (>1GB) | Compress first: `gzip file` or use `rsync --progress` |
| Transfer interrupted | Resume with `rsync --partial --progress` |
| Tailscale down on Mac | Use GCS signed URL or HTTP server fallback |

## Delivery Log
Track all deliveries in `~/.openclaw/memory/delivery-log.json`:
```json
{
  "deliveries": [
    {
      "date": "2026-04-05T14:30:00",
      "file": "kling-showcase.mp4",
      "size": "12.3 MB",
      "method": "scp-tailscale",
      "status": "delivered",
      "attempts": 1
    }
  ]
}
```

## Output Format
```
FILE DELIVERY:
- File: [filename] ([size])
- Method: [SCP / GCS / HTTP / Pending]
- Attempts: [count]
- Status: Delivered / Failed (using fallback) / Pending
- Location: /Users/tonny/Downloads/[filename]
```
