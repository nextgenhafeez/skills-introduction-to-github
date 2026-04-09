---
name: file-delivery
description: Deliver files from VM to Boss's Mac via SCP/Tailscale
triggers:
  - "send me", "deliver", "transfer", "download"
  - "send the file", "send the video", "send the image"
  - After any content generation Boss requested
---

# SKILL: File Delivery to Boss's Mac

## Connection Details
- **Mac Tailscale IP**: `100.105.165.84` (static)
- **Mac username**: `tonny`
- **Destination**: `/Users/tonny/Downloads/`
- **SSH key**: `~/.ssh/id_ed25519`

## Delivery Steps
1. Verify file exists: `ls -lh /path/to/file`
2. SCP: `scp -o ConnectTimeout=15 /path/to/file tonny@100.105.165.84:/Users/tonny/Downloads/`
3. Verify: `ssh -o ConnectTimeout=15 tonny@100.105.165.84 "ls -lh /Users/tonny/Downloads/$(basename /path/to/file)"`
4. Confirm to Boss: "File delivered to Downloads: **filename** (size)"

## VM File Paths
Videos: `/home/tonny/content/videos/` | Images: `/home/tonny/content/images/` | General: `/home/tonny/content/`

## Rules
- ALWAYS use Tailscale IP 100.105.165.84 (never local IP)
- Verify file exists before sending, confirm delivery with filename+size
- For >100MB, warn Boss it may take a moment
- NEVER delete source file after delivery

## Fallback Methods (after 3 SCP retries with 30s delay)
1. **GCS**: `gsutil cp` to gs://blacklayers-temp/ → `gsutil signurl -d 24h` → send URL via WhatsApp
2. **HTTP**: `python3 -m http.server 9090` on VM → send http://34.132.116.116:9090/filename → kill after download
3. **Save**: Copy to ~/content/pending-delivery/ → notify Boss, deliver when Mac online

## Troubleshooting
Connection refused → check `tailscale status` → check SSH with -v flag → Mac may be asleep (tell Boss)

## Delivery Log
Track in `~/.openclaw/memory/delivery-log.json`: date, file, size, method, status, attempts.
