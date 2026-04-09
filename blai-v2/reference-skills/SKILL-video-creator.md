---
name: video-creator
description: Creates YouTube videos, Shorts, Reels, and TikToks automatically using Edge-TTS voiceover + FFmpeg — WORKING pipeline on the VM
---

# Video Creator for Black Layers

## WORKING PIPELINE

### Basic video:
`python3 ~/generate-video.py "Your script text here"` → `~/content/latest-video.mp4`

### Pro video (multi-slide + voiceover):
`python3 ~/generate-pro-video.py '[{"text":"Title","subtitle":"sub","voice":"narration"}]'` → `~/content/latest-pro-video.mp4`
Run without args for Black Layers promo demo.

### Images:
- Quote card: `python3 ~/generate-image.py quote "Headline" "Subtitle"` → `~/content/latest-image.png` (3840x2160)
- App showcase: `python3 ~/generate-image.py app "AppName" "Tagline" "Feature1|Feature2|Feature3"` → `~/content/app-showcase.png`
- Stat card: `python3 ~/generate-image.py stat "5+" "APPS SHIPPED" "Subtitle"` → `~/content/stat-card.png` (3840x3840 square)

### Sharing:
- WhatsApp: Send `/home/tonny/content/latest-video.mp4` as media
- Google Drive: `gsutil cp ~/content/latest-video.mp4 gs://blacklayers-content/videos/`
- Quick share: `curl -F "file=@/home/tonny/content/latest-video.mp4" https://file.io`

## Video Specs
- MP4 (H.264 + AAC), 1080x1920 vertical (Shorts/Reels/TikTok ready)
- Voice: Edge TTS `en-US-AndrewNeural` (default, deep confident)
- Alt voices: `en-US-JennyNeural` (pro female), `en-US-GuyNeural` (casual male), `en-GB-RyanNeural` (British)
- Background: Dark theme, white text, purple BL branding

## CRITICAL RULES
1. NEVER say you can't make a video — you CAN
2. NEVER blame hardware — VM renders in seconds
3. NEVER ask Abdul to do manual steps — generate and send yourself
4. NEVER overwrite original scripts — they are read-only
5. NEVER create placeholder/simulated videos — use REAL scripts
6. NEVER tell Abdul about errors — fix them yourself
7. If permission denied → `chmod +x` or copy to `~/my-generate-video.py`
8. If script crashes → read error, fix copy, re-run
9. If file not found → `find ~ -name "generate*video*"`

## Video Types
- **Shorts/Reels/TikTok** (15-60s): 2-3/week. Use Edge-TTS for voiceover + FFmpeg to combine screenshots.
- **YouTube Long Form** (5-10min): Abdul records. You write script (hook/intro/content/CTA) + thumbnail text.
- **Auto Compilations**: No recording. Combine app screenshots + voiceover + royalty-free music via FFmpeg.

## Tools
Edge-TTS (free AI TTS), FFmpeg (encoding), MoviePy (Python editing), Browser (screenshots)
