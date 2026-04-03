---
name: tiktok-realistic-video
description: Step-by-step guide to create realistic AI videos and post on TikTok — no excuses, just execute
---

# TikTok Realistic AI Video — Full Pipeline

## STEP 1: SIGN UP FOR FREE AI VIDEO ACCOUNTS

Do this ONCE, save the API keys:

### HaiLuo (Best realistic quality — FREE)
1. Go to https://hailuoai.video
2. Sign up with email
3. You get ~10 free video generations per day
4. Use the web interface OR the MiniMax API

### Kling AI (Second best — FREE)
1. Go to https://klingai.com
2. Sign up with email
3. You get ~66 free credits per day

### SiliconFlow (API access to ALL models — cheapest)
1. Go to https://siliconflow.cn
2. Sign up — get free credits
3. API key gives access to Wan 2.1, CogVideoX, etc.

---

## STEP 2: CREATE REALISTIC VIDEO

### Method A: HaiLuo Web (Easiest — do this first)
1. Open browser to hailuoai.video
2. Enter prompt from the prompt library below
3. Download the MP4
4. Save to ~/content/tiktok-video.mp4

### Method B: MiniMax API (Automated)
```python
import requests, time, os

API_KEY = os.getenv("MINIMAX_API_KEY", "your_key_here")
HEADERS = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}

def generate_video(prompt):
    resp = requests.post(
        "https://api.minimax.chat/v1/video_generation",
        headers=HEADERS,
        json={"model": "video-01-live", "prompt": prompt}
    )
    task_id = resp.json().get("task_id")
    print(f"Task submitted: {task_id}")
    
    for i in range(60):
        time.sleep(10)
        status = requests.get(
            f"https://api.minimax.chat/v1/query/video_generation?task_id={task_id}",
            headers=HEADERS
        ).json()
        if status.get("status") == "Success":
            video_url = status["file_id"]
            video = requests.get(video_url)
            with open(os.path.expanduser("~/content/tiktok-video.mp4"), "wb") as f:
                f.write(video.content)
            print("Video saved to ~/content/tiktok-video.mp4")
            return True
        elif status.get("status") == "Fail":
            return False
        print(f"Waiting... ({i*10}s)")
    return False

prompts = {
    "app_showcase": "Cinematic slow motion close-up of hands holding an iPhone 16 Pro, scrolling through a beautifully designed iOS app with smooth animations, soft natural lighting from a window, shallow depth of field, photorealistic, 4K quality",
    "dev_workspace": "Tracking shot across a clean modern desk, MacBook Pro screen showing Xcode with Swift code, AirPods and coffee beside it, warm ambient lighting, cinematic color grading, ultra realistic",
    "app_launch": "Dramatic reveal shot, iPhone on a sleek black surface, app icon appears on screen with a soft glow, camera slowly dollies in, dark moody lighting with blue accent lights, professional product video style",
    "coding_magic": "Close-up of fingers typing on MacBook keyboard, code reflecting on the developer's glasses, matrix-style code particles floating in the air, cinematic blue and purple lighting, hyper-detailed"
}

generate_video(prompts["app_showcase"])
```

### Method C: Wan 2.1 via SiliconFlow (Free + Automated)
```python
import requests, os

API_KEY = os.getenv("SILICONFLOW_API_KEY", "your_key_here")

resp = requests.post(
    "https://api.siliconflow.cn/v1/video/generations",
    headers={"Authorization": f"Bearer {API_KEY}"},
    json={
        "model": "Wan-AI/Wan2.1-T2V-14B",
        "prompt": "Cinematic dolly shot, iPhone floating in dark studio, beautiful app on screen, volumetric purple and blue lighting, photorealistic",
        "resolution": "1080x1920",
        "duration": 5
    }
)
print(resp.json())
```

---

## STEP 3: ADD TEXT + AUDIO (Make it TikTok-ready)

```bash
# Add text overlay
ffmpeg -i ~/content/tiktok-video.mp4 \
  -vf "drawtext=text='We built this app in 48 hours':fontsize=48:fontcolor=white:borderw=3:bordercolor=black:x=(w-text_w)/2:y=100:fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" \
  -c:a copy ~/content/tiktok-text.mp4

# Add voiceover
edge-tts --voice "en-US-AndrewNeural" --text "This app was built in just 48 hours. Here is how we did it at Black Layers." --write-media ~/content/voiceover.mp3

# Combine video + voiceover
ffmpeg -i ~/content/tiktok-text.mp4 -i ~/content/voiceover.mp3 \
  -c:v copy -c:a aac -shortest ~/content/tiktok-final.mp4
```

---

## STEP 4: POST TO TIKTOK

### Method A: Browser Automation (No API key needed)
1. Open browser to tiktok.com
2. Login with session cookies (already in workspace)
3. Navigate to tiktok.com/upload
4. Upload ~/content/tiktok-final.mp4
5. Add caption + hashtags
6. Click Post

### Method B: Via Make.com Webhook (Already Set Up)
```bash
curl -X POST "https://hook.us1.make.com/YOUR_WEBHOOK_ID" \
  -F "video=@/home/tonny/content/tiktok-final.mp4" \
  -F "caption=We built this iOS app in 48 hours #tech #iosdev #blacklayers" \
  -F "platform=tiktok"
```

### Method C: TikTok Developer API
Register at developers.tiktok.com, get OAuth token, use Content Posting API to upload programmatically.

---

## STEP 5: DAILY AUTOMATION

```bash
# Cron: auto-generate and post 2 videos daily
# 9 AM — morning post
0 9 * * * python3 /home/tonny/tiktok-video-gen.py >> /tmp/tiktok-auto.log 2>&1
# 7 PM — evening post
0 19 * * * python3 /home/tonny/tiktok-video-gen.py >> /tmp/tiktok-auto.log 2>&1
```

---

## REALISTIC PROMPT LIBRARY (Copy-Paste Ready)

### Product / App Showcase:
1. `Cinematic slow-motion, hands holding iPhone 16 Pro in a dark studio, beautiful iOS app on screen with smooth scrolling, soft blue rim lighting, shallow depth of field, photorealistic 4K`
2. `Orbital camera shot around a floating iPhone, holographic app UI projecting from the screen, dark environment with purple and cyan particle effects, futuristic tech commercial style`
3. `Top-down close-up of iPhone on marble desk, finger tapping through an elegant app interface, natural sunlight casting soft shadows, product photography style, ultra realistic`

### Developer / Behind the Scenes:
4. `Tracking shot, developer sitting in a modern office typing Swift code on MacBook Pro, multiple monitors showing Xcode and Figma, golden hour light, documentary style, photorealistic`
5. `Time-lapse style, empty desk to full workstation setup, code appearing on screen, apps being built frame by frame, clean modern office, warm lighting`

### Viral Hook Shots:
6. `Snap zoom into MacBook screen, code transforming into a beautiful mobile app in real-time, digital particles and light trails, dark background with electric blue accents, high energy`
7. `Dramatic slow reveal, black screen to lit iPhone showing a stunning app, camera pulling back to reveal modern office, cinematic tension, movie trailer style`
8. `Split screen, left side messy wireframe sketch, right side polished iOS app, morphing transition between them, clean white background, satisfying transformation`

---

## EXECUTION RULES — NO EXCUSES

1. When Boss says "make a TikTok video" -> run generation immediately
2. When generation fails -> switch model silently (HaiLuo -> Kling -> Wan -> CogVideo)
3. Always add text overlay + voiceover before posting
4. Always use vertical format 1080x1920
5. Post to TikTok + YouTube Shorts + Instagram Reels simultaneously
6. Never ask which prompt — pick the best one and generate
7. Send the final video to Boss on WhatsApp immediately
8. Never explain how video generation works — just DO IT
