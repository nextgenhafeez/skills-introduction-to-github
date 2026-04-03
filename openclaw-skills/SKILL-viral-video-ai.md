---
name: viral-video-ai
description: Generate viral videos using free Chinese AI video generators + prompting for max views
---

# Viral AI Video Creation — Free Chinese Models

## TOP FREE AI VIDEO GENERATORS (Use These)

### 1. HaiLuo / MiniMax (BEST FREE QUALITY)
- URL: https://hailuoai.video
- Free: ~10 videos/day, no watermark
- API: POST https://api.minimax.chat/v1/video_generation
- Model: video-01-live
- Best for: Cinematic, smooth motion content

### 2. Kling AI (BEST OVERALL)
- URL: https://klingai.com
- Free: ~66 credits/day (~5-10 clips)
- API: Available via Replicate / FAL.ai
- Best for: Realistic human motion, high quality

### 3. Wan 2.1 by Alibaba (BEST FOR AUTOMATION — OPEN SOURCE)
- HuggingFace: Wan-AI/Wan2.1-T2V-14B (big) or Wan2.1-T2V-1.3B (small, runs on Mac GPU)
- License: Apache 2.0 — unlimited free use
- API: DashScope (Alibaba), Replicate, SiliconFlow
- Best for: Scale automation, zero cost if self-hosted

### 4. CogVideoX by Zhipu AI (OPEN SOURCE)
- GitHub: THUDM/CogVideo
- Free: Fully open source (2B and 5B models)
- Best for: Budget automation

### 5. Hunyuan Video by Tencent (OPEN SOURCE)
- GitHub: Tencent/HunyuanVideo
- Free: Fully open source, 13B model
- Best for: No-cost high quality generation

---

## PROMPTING FORMULA FOR VIRAL CONTENT

Structure:
`[Camera movement], [subject], [action], [environment], [lighting], [style]`

### Black Layers Prompt Templates:

**App Showcase (use for portfolio content):**
```
Slow cinematic dolly shot, a sleek iPhone 16 floating in mid-air displaying a beautiful iOS app interface, particles of light emanating from the screen, dark moody studio environment with volumetric blue and purple lighting, photorealistic, 4K
```

**Tech Authority / Founder Content:**
```
Medium close-up tracking shot, a confident developer typing on a MacBook Pro in a modern minimalist office, soft golden hour light streaming through floor-to-ceiling windows, shallow depth of field, cinematic color grading
```

**Attention Hook (first 1 second):**
```
Extreme close-up snap zoom into a smartphone screen showing code transforming into a beautiful app UI, electric blue energy particles, dark background, dramatic lighting, hyper-detailed
```

**Transformation / Before-After:**
```
Split screen morphing from rough wireframe sketch to polished iOS app interface, smooth 3D rotation, studio lighting with blue and white tones, professional product visualization
```

### Prompting Rules:
1. Front-load the visual hook — AI models weight the beginning more heavily
2. Always specify camera movement: "dolly in", "orbital shot", "tracking shot"
3. Include lighting: "volumetric", "neon rim light", "golden hour"
4. Describe what the viewer SEES, not metaphors
5. Keep prompts 30-80 words — too short = generic, too long = confused

---

## MAXIMIZING VIEWS — ALGORITHM RULES

### Hook Formula (CRITICAL — first 0.5 seconds):
- First frame must be visually arresting
- Start MID-ACTION, never with a title card
- Use text overlay: provocative question > statement

### Optimal Length:
- YouTube Shorts: 15-30 seconds
- TikTok: 7-15 seconds
- Instagram Reels: 15-30 seconds

### Loop Structure:
- Make the END connect visually to the BEGINNING
- Platforms reward re-watches — looping = more views

### Posting Strategy:
- Post 2-3x daily at peak hours (7-9am, 12-1pm, 7-10pm target timezone)
- Add TRENDING AUDIO (biggest algorithmic boost)
- 3-5 hashtags max: mix broad (#tech #AI) + niche (#iosdeveloper #appdev)
- End with "Follow for more" or a question to boost comments

### What Goes Viral with AI Video:
- "Satisfying" transformation clips (code → polished app)
- Tech "magic" visuals (floating devices, futuristic interfaces)
- Before/after reveals
- AI-generated cinematic versions of mundane dev tasks

---

## AUTOMATION PIPELINE

### Quick Generation (use MiniMax API):
```python
import requests

API_KEY = "your_minimax_key"
headers = {"Authorization": f"Bearer {API_KEY}"}

response = requests.post(
    "https://api.minimax.chat/v1/video_generation",
    headers=headers,
    json={
        "model": "video-01-live",
        "prompt": "Slow cinematic dolly shot, iPhone 16 floating displaying iOS app, particles of light, dark studio, volumetric blue and purple lighting, photorealistic"
    }
)
task_id = response.json()["task_id"]
# Poll for completion, then download video URL
```

### Free Generation (use Wan 2.1 via SiliconFlow):
```python
# SiliconFlow API — very cheap, hosts all open-source Chinese models
import requests

response = requests.post(
    "https://api.siliconflow.cn/v1/video/generations",
    headers={"Authorization": "Bearer YOUR_KEY"},
    json={
        "model": "Wan-AI/Wan2.1-T2V-14B",
        "prompt": "your prompt here",
        "resolution": "1080x1920"
    }
)
```

### Full Daily Pipeline:
1. Generate 3 video clips via API (morning cron job)
2. FFmpeg adds text overlay + trending audio
3. Upload to YouTube Shorts, TikTok, Instagram Reels
4. Track analytics — feed best performers back into prompts
5. Report results to boss on WhatsApp

---

## QUICK REFERENCE

| Model | Free? | Quality | API | Best For |
|-------|-------|---------|-----|----------|
| HaiLuo/MiniMax | ~10/day | ★★★★★ | Yes | Cinematic |
| Kling | ~5-10/day | ★★★★★ | Replicate | Realism |
| Wan 2.1 | Unlimited | ★★★★☆ | Yes | Automation |
| CogVideoX | Unlimited | ★★★☆☆ | Self-host | Budget |
| HunyuanVideo | Unlimited | ★★★★☆ | Self-host | Free quality |

