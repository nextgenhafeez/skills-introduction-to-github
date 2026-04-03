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
