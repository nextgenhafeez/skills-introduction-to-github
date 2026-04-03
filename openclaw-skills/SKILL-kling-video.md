# SKILL: Kling 3.0 Video Generator + Social Media Poster

## Purpose
Generate professional AI videos using Kling 3.0 API, then post to TikTok, YouTube Shorts, and Instagram Reels. Deliver video to Boss's Mac via SCP.

## Setup (One-Time)

### 1. Get Kling API Keys
1. Go to https://app.klingai.com/global/dev
2. Sign up with Google/email
3. Create a new API key — you get:
   - **Access Key (AK)** — public identifier
   - **Secret Key (SK)** — shown once, save it
4. Store on VM:
```bash
echo 'export KLING_ACCESS_KEY="your_ak_here"' >> ~/.bashrc
echo 'export KLING_SECRET_KEY="your_sk_here"' >> ~/.bashrc
source ~/.bashrc
```

### 2. Install Dependencies
```bash
pip install PyJWT requests
```

### 3. Free Tier
- **66 free credits/day** (resets every 24 hours, does NOT roll over)
- 5-second video = 10 credits (standard) / 35 credits (pro)
- 10-second video = 20 credits (standard) / 70 credits (pro)
- Free tier = watermarked, max 5 seconds, 720p
- Pro plan ($25.99/mo) = 3,000 credits, no watermark, 1080p+

---

## Video Generation Script

Save as `~/scripts/kling-video.py` on the VM:

```python
#!/usr/bin/env python3
"""
Kling 3.0 Video Generator for Black Layers
Usage: python3 kling-video.py "prompt" [options]
"""

import os
import sys
import time
import json
import argparse
import requests
import jwt

# --- Config ---
AK = os.environ.get("KLING_ACCESS_KEY", "")
SK = os.environ.get("KLING_SECRET_KEY", "")
BASE_URL = "https://api.klingai.com"
OUTPUT_DIR = os.path.expanduser("~/content/videos")
MAC_IP = "100.105.165.84"
MAC_USER = "tonny"
MAC_DOWNLOADS = f"/Users/{MAC_USER}/Downloads"

def get_token():
    """Generate JWT token for Kling API"""
    if not AK or not SK:
        print("ERROR: Set KLING_ACCESS_KEY and KLING_SECRET_KEY in env")
        sys.exit(1)
    headers = {"alg": "HS256", "typ": "JWT"}
    payload = {
        "iss": AK,
        "exp": int(time.time()) + 1800,
        "nbf": int(time.time()) - 5,
        "iat": int(time.time())
    }
    return jwt.encode(payload, SK, algorithm="HS256", headers=headers)

def create_video(prompt, negative_prompt="", duration="5", aspect="9:16", mode="std", cfg=0.7):
    """Submit text-to-video generation task"""
    token = get_token()
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    body = {
        "model_name": "kling-v3",
        "prompt": prompt,
        "negative_prompt": negative_prompt or "blurry, distorted faces, text artifacts, watermark, low quality, cartoon, anime, static",
        "duration": str(duration),
        "aspect_ratio": aspect,
        "mode": mode,
        "cfg_scale": cfg
    }
    resp = requests.post(f"{BASE_URL}/v1/videos/text2video", headers=headers, json=body)
    resp.raise_for_status()
    data = resp.json()
    if data.get("code") != 0:
        print(f"API Error: {data}")
        sys.exit(1)
    task_id = data["data"]["task_id"]
    print(f"Task created: {task_id}")
    return task_id

def create_video_from_image(image_url, prompt, duration="5", aspect="9:16", mode="std"):
    """Submit image-to-video generation task"""
    token = get_token()
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    body = {
        "model_name": "kling-v3",
        "image": image_url,
        "prompt": prompt,
        "negative_prompt": "blurry, distorted, low quality, cartoon, anime",
        "duration": str(duration),
        "aspect_ratio": aspect,
        "mode": mode
    }
    resp = requests.post(f"{BASE_URL}/v1/videos/image2video", headers=headers, json=body)
    resp.raise_for_status()
    data = resp.json()
    if data.get("code") != 0:
        print(f"API Error: {data}")
        sys.exit(1)
    task_id = data["data"]["task_id"]
    print(f"Image-to-video task created: {task_id}")
    return task_id

def poll_task(task_id, endpoint="text2video", max_wait=300):
    """Poll until video is ready (max 5 minutes)"""
    token = get_token()
    headers = {"Authorization": f"Bearer {token}"}
    start = time.time()
    while time.time() - start < max_wait:
        resp = requests.get(f"{BASE_URL}/v1/videos/{endpoint}/{task_id}", headers=headers)
        data = resp.json()
        status = data["data"]["task_status"]
        print(f"  Status: {status} ({int(time.time() - start)}s)")
        if status == "succeed":
            video_url = data["data"]["task_result"]["videos"][0]["url"]
            return video_url
        elif status == "failed":
            print(f"FAILED: {data['data'].get('task_status_msg', 'unknown')}")
            return None
        time.sleep(8)
    print("TIMEOUT: Video generation took too long")
    return None

def download_video(url, filename):
    """Download video to local storage"""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    filepath = os.path.join(OUTPUT_DIR, filename)
    resp = requests.get(url, stream=True)
    with open(filepath, "wb") as f:
        for chunk in resp.iter_content(chunk_size=8192):
            f.write(chunk)
    size_mb = os.path.getsize(filepath) / (1024 * 1024)
    print(f"Downloaded: {filepath} ({size_mb:.1f} MB)")
    return filepath

def deliver_to_mac(filepath):
    """SCP file to Boss's Mac Downloads"""
    filename = os.path.basename(filepath)
    cmd = f'scp -o ConnectTimeout=15 "{filepath}" {MAC_USER}@{MAC_IP}:{MAC_DOWNLOADS}/{filename}'
    result = os.system(cmd)
    if result == 0:
        print(f"Delivered to Mac: ~/Downloads/{filename}")
    else:
        print("WARNING: SCP delivery failed — check Tailscale connection")

def add_voiceover(video_path, script_text, output_path=None):
    """Add Edge-TTS voiceover to video"""
    if not output_path:
        base = os.path.splitext(video_path)[0]
        output_path = f"{base}_voiced.mp4"
    audio_path = "/tmp/voiceover.mp3"
    
    # Generate TTS
    os.system(f'edge-tts --voice "en-US-AndrewNeural" --text "{script_text}" --write-media {audio_path}')
    
    # Merge audio with video
    os.system(f'ffmpeg -y -i "{video_path}" -i {audio_path} -c:v copy -c:a aac -map 0:v -map 1:a -shortest "{output_path}"')
    
    if os.path.exists(output_path):
        print(f"Voiceover added: {output_path}")
        return output_path
    return video_path

def main():
    parser = argparse.ArgumentParser(description="Kling 3.0 Video Generator")
    parser.add_argument("prompt", help="Video prompt/description")
    parser.add_argument("--duration", default="5", choices=["3","5","10","15"], help="Video duration in seconds")
    parser.add_argument("--aspect", default="9:16", choices=["16:9","9:16","1:1"], help="Aspect ratio")
    parser.add_argument("--mode", default="std", choices=["std","pro"], help="Quality mode")
    parser.add_argument("--cfg", type=float, default=0.7, help="Prompt adherence 0.0-1.0")
    parser.add_argument("--image", default=None, help="Image URL for image-to-video")
    parser.add_argument("--name", default=None, help="Output filename (without .mp4)")
    parser.add_argument("--voiceover", default=None, help="TTS script for voiceover")
    parser.add_argument("--deliver", action="store_true", help="SCP to Boss's Mac")
    parser.add_argument("--no-deliver", action="store_true", help="Skip SCP delivery")
    args = parser.parse_args()

    # Generate filename
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    filename = f"{args.name or 'kling'}_{timestamp}.mp4"

    # Create video task
    if args.image:
        task_id = create_video_from_image(args.image, args.prompt, args.duration, args.aspect, args.mode)
        endpoint = "image2video"
    else:
        task_id = create_video(args.prompt, duration=args.duration, aspect=args.aspect, mode=args.mode, cfg=args.cfg)
        endpoint = "text2video"

    # Wait for completion
    video_url = poll_task(task_id, endpoint)
    if not video_url:
        sys.exit(1)

    # Download
    filepath = download_video(video_url, filename)

    # Add voiceover if requested
    if args.voiceover:
        filepath = add_voiceover(filepath, args.voiceover)

    # Deliver to Mac
    if not args.no_deliver:
        deliver_to_mac(filepath)

    print(f"\nDONE: {filepath}")
    return filepath

if __name__ == "__main__":
    main()
```

---

## How to Use

### Basic — Text to Video
```bash
python3 ~/scripts/kling-video.py "A developer sitting at a dark desk, typing on a MacBook Pro, neon code reflecting on their glasses, cinematic lighting, 4K" --duration 5 --aspect 9:16 --deliver
```

### Image to Video (animate a still image)
```bash
python3 ~/scripts/kling-video.py "Camera slowly zooms in, person turns to face camera and smiles" --image "https://example.com/photo.jpg" --duration 5 --deliver
```

### With Voiceover
```bash
python3 ~/scripts/kling-video.py "A sleek iOS app being built on screen, code compiling, app launching on iPhone" --voiceover "At Black Layers, we build iOS apps that perform. From idea to App Store, we handle everything." --deliver
```

### Pro Quality (uses more credits)
```bash
python3 ~/scripts/kling-video.py "prompt here" --mode pro --duration 10 --deliver
```

---

## Prompt Strategy for Realistic Videos

### Structure Every Prompt Like This:
```
[SUBJECT] + [ACTION] + [ENVIRONMENT] + [LIGHTING] + [CAMERA] + [STYLE]
```

### Example Prompts for Black Layers Content:

**App Showcase:**
"Close-up of hands holding an iPhone 15 Pro, scrolling through a beautifully designed food ordering app, dark UI with orange accents, shallow depth of field, warm studio lighting, 4K cinematic"

**Developer at Work:**
"Medium shot of a developer coding Swift on a MacBook Pro in a modern dark office, multiple monitors showing Xcode, blue ambient lighting reflecting off screens, camera slowly dollies in, professional documentary style"

**AI Agent Demo:**
"Split screen showing a WhatsApp chat on the left with messages appearing automatically, and a server terminal on the right processing requests, dark theme, green text on black, tech documentary style"

**Brand Identity:**
"Elegant 3D text 'Black Layers' materializing from dark particles, black and white color scheme, minimal design, camera orbits around the text, premium corporate style"

### Negative Prompt (always use):
```
blurry, distorted faces, text artifacts, watermark, low quality, cartoon, anime, static, jittery, flickering
```

---

## Post-Processing Pipeline

After Kling generates the raw video:

### 1. Add BL Branding Overlay
```bash
ffmpeg -y -i input.mp4 -i ~/content/images/bl-watermark.png \
  -filter_complex "overlay=W-w-20:H-h-20" \
  -c:a copy output_branded.mp4
```

### 2. Add Text Caption
```bash
ffmpeg -y -i input.mp4 \
  -vf "drawtext=text='Black Layers':fontsize=36:fontcolor=white:x=(w-text_w)/2:y=h-80:font=Arial:borderw=2:bordercolor=black" \
  -c:a copy output_captioned.mp4
```

### 3. Add Voiceover
```bash
edge-tts --voice "en-US-AndrewNeural" --text "Your script here" --write-media /tmp/voice.mp3
ffmpeg -y -i input.mp4 -i /tmp/voice.mp3 -c:v copy -c:a aac -map 0:v -map 1:a -shortest output_final.mp4
```

---

## Social Media Posting

### Option A: Make.com Webhook (Recommended)
```bash
curl -X POST "https://hook.us1.make.com/YOUR_WEBHOOK_ID" \
  -F "video=@/path/to/video.mp4" \
  -F "caption=Your caption here" \
  -F "platforms=tiktok,youtube,instagram"
```

### Option B: Direct Upload via APIs
Set up separately for each platform — requires OAuth tokens.

### Option C: Deliver to Boss + He Posts
```bash
scp -o ConnectTimeout=15 /path/to/video.mp4 tonny@100.105.165.84:/Users/tonny/Downloads/
```
Then notify Boss on WhatsApp with caption text.

---

## Daily Automation (Cron)

Add to crontab for automated daily video posts:
```bash
# 9 AM UTC — morning post
0 9 * * * cd ~/scripts && python3 kling-video.py "$(python3 daily-prompt.py morning)" --duration 5 --aspect 9:16 --voiceover "$(python3 daily-script.py morning)" --deliver --name "bl_morning" >> ~/logs/kling.log 2>&1

# 7 PM UTC — evening post
0 19 * * * cd ~/scripts && python3 kling-video.py "$(python3 daily-prompt.py evening)" --duration 5 --aspect 9:16 --voiceover "$(python3 daily-script.py evening)" --deliver --name "bl_evening" >> ~/logs/kling.log 2>&1
```

---

## Credit Budget Management

| Action | Credits | Videos/Day (Free 66 credits) |
|--------|---------|------------------------------|
| 5s Standard | 10 | 6 videos |
| 5s Pro | 35 | 1 video |
| 10s Standard | 20 | 3 videos |
| 10s Pro | 70 | 0 (need paid plan) |

**Strategy for free tier:** Use Standard mode, 5-second clips, generate 2-3 per day. Save Pro mode for important posts.

---

## Rules
- ALWAYS use `--aspect 9:16` for TikTok/Reels/Shorts (vertical)
- ALWAYS use `--aspect 16:9` for YouTube long-form or LinkedIn
- ALWAYS include negative prompt to avoid artifacts
- ALWAYS deliver to Boss's Mac after generation (use --deliver flag)
- NEVER exceed daily credit budget — track usage
- Keep prompt under 2500 characters
- Download videos immediately — Kling deletes after 30 days
- If API returns rate_limit error, wait 60 seconds and retry once
- If task fails, try reducing duration or switching to std mode
