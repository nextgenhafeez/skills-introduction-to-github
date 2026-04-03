---
name: video-creator
description: Creates YouTube videos, Shorts, Reels, and TikToks automatically using Edge-TTS voiceover + FFmpeg — WORKING pipeline on the VM
---

# Video Creator for Black Layers

You create video content automatically for Black Layers.

## WORKING VIDEO PIPELINE (Use This!)

You have a tested, working video generator at `~/generate-video.py` on the VM.

### How to generate a video:
```bash
python3 ~/generate-video.py "Your script text here"
```
This outputs: `~/content/latest-video.mp4`

### How to send it to Abdul on WhatsApp:
After generating, the file is at `/home/tonny/content/latest-video.mp4`.
Send it as a media message on WhatsApp.

### How to upload to Google Drive and share link:
```bash
# Upload to Google Drive (if gsutil is configured)
gsutil cp ~/content/latest-video.mp4 gs://blacklayers-content/videos/
# Or use curl to upload to file.io for quick sharing:
curl -F "file=@/home/tonny/content/latest-video.mp4" https://file.io
```

### Video specs:
- Format: MP4 (H.264 + AAC)
- Resolution: 1080x1920 (vertical, perfect for Shorts/Reels/TikTok)
- Voice: Microsoft Edge TTS (en-US-AndrewNeural — deep, confident)
- Background: Dark theme with white text + purple Black Layers branding
- Duration: Based on script length (typically 8-15 seconds)

### CRITICAL RULES — READ THESE CAREFULLY:
1. **NEVER tell Abdul you can't make a video** — you CAN, always
2. **NEVER blame hardware** — the VM renders videos in seconds
3. **NEVER ask Abdul to do manual steps** — generate and send it yourself
4. **NEVER overwrite or modify the original scripts** — they are read-only for a reason
5. **NEVER create "placeholder" or "simulated" videos** — use the REAL scripts
6. **NEVER tell Abdul about errors** — fix them yourself (see error-recovery skill)
7. Just run the command and send the result. No excuses. No narration.

### If Something Goes Wrong:
- Permission denied → `chmod +x` or copy script to `~/my-generate-video.py`
- Script crashes → Read error, fix the copy, run again
- File not found → Search with `find ~ -name "generate*video*"`
- Output looks wrong → Re-run with different params
- **DO NOT MESSAGE ABDUL ABOUT ANY OF THIS. Fix it and send the video.**

---

## PRO VIDEO GENERATOR (Multi-slide + Voiceover)

For professional videos with multiple slides and transitions:

```bash
python3 ~/generate-pro-video.py '[{"text":"Slide 1 Title","subtitle":"subtitle","voice":"What the AI says"},{"text":"Slide 2","subtitle":"more info","voice":"Voice for slide 2"}]'
```

Output: `~/content/latest-pro-video.mp4`

**Demo (run without arguments for a Black Layers promo):**
```bash
python3 ~/generate-pro-video.py
```

### Pro video specs:
- 4 slides with dark theme + purple branding
- Professional AI voiceover (Edge TTS)
- 1080x1920 vertical (Shorts/Reels/TikTok ready)
- ~15-20 seconds, perfect retention length

---

## 4K IMAGE GENERATOR

Three image types available:

### 1. Quote Card (for LinkedIn, Twitter, Instagram):
```bash
python3 ~/generate-image.py quote "Your Headline Here" "Subtitle text here"
```
Output: `~/content/latest-image.png` (3840x2160, 4K)

### 2. App Showcase (portfolio pieces):
```bash
python3 ~/generate-image.py app "AdClose" "Smart Ad Management" "Block unwanted ads|Save battery|Privacy focused"
```
Output: `~/content/app-showcase.png` (3840x2160, 4K)

### 3. Stat Card (engagement posts for Instagram):
```bash
python3 ~/generate-image.py stat "5+" "APPS SHIPPED" "From idea to App Store"
```
Output: `~/content/stat-card.png` (3840x3840, square for Instagram)

---

## WORKFLOW: How to create and post content

1. **Generate image:** `python3 ~/generate-image.py quote "headline" "subtitle"`
2. **Generate video:** `python3 ~/generate-pro-video.py '[slides json]'`
3. **Send to Abdul on WhatsApp** (attach the file)
4. **Post via Make.com webhook** (attach media URL)

## Available AI Voices:
- `en-US-AndrewNeural` — Deep, confident male (DEFAULT)
- `en-US-JennyNeural` — Professional female
- `en-US-GuyNeural` — Casual male
- `en-GB-RyanNeural` — British male

## Tools Available
- **Edge-TTS**: Free AI text-to-speech (Microsoft voices)
- **FFmpeg**: Video encoding and composition
- **MoviePy**: Python video editing
- **Browser**: Screenshot app pages, download assets

## Video Types

### 1. YouTube Shorts / Reels / TikTok (15-60 seconds)
Best for virality. Create 2-3 per week.

**Process:**
```bash
# 1. Write script (5-8 sentences)
# 2. Generate voiceover
edge-tts --voice "en-US-GuyNeural" --text "script here" --write-media voiceover.mp3

# 3. Take screenshots of apps from App Store / website
# Use browser automation to screenshot blacklayers.ca, app pages

# 4. Combine into video
ffmpeg -framerate 1/3 -i screenshot_%d.png -i voiceover.mp3 \
  -c:v libx264 -pix_fmt yuv420p -shortest output.mp4
```

**Short Video Templates:**

Template A — "Did You Know?"
```
[Screenshot of AdClose]
"Did you know there's an ad blocker making $10,000 every month?"

[Screenshot of App Store page]
"It's called AdClose, and we built it at Black Layers."

[Screenshot of revenue/downloads]
"Here's what we did differently..."

[Text: "Follow for more" + blacklayers.ca]
```

Template B — "Quick Tip"
```
[Screen recording of Xcode]
"Here's a SwiftUI trick most developers don't know..."

[Code snippet screenshot]
"Use the .task modifier instead of .onAppear for async work."

[Before/after comparison]
"It automatically cancels when the view disappears. Clean code."

[Text: "Follow @blacklayers for daily tips"]
```

### 2. YouTube Long Form (5-10 minutes)
Abdul records these. You write the script and create the thumbnail.

**Script Format:**
```
TITLE: [SEO-optimized title]
THUMBNAIL: [Text overlay suggestion for Canva]

[0:00 - 0:10] HOOK
"What if I told you a single app could make $10,000 a month?
That's exactly what happened with AdClose."

[0:10 - 0:40] INTRO
"I'm Abdul from Black Layers. We build iOS apps for startups
and businesses. Today I'm going to show you..."

[0:40 - 5:00] MAIN CONTENT
[Teach, show, demonstrate — use screen recordings and screenshots]

[5:00 - 5:30] CTA
"If you found this helpful, subscribe and hit the bell.
Need an app built? Visit blacklayers.ca. Link in description."

DESCRIPTION:
[Full SEO description with timestamps, links, keywords]

TAGS:
iOS development, app development, SwiftUI tutorial, mobile app,
Black Layers, hire app developer, Swift programming
```

### 3. Auto-Generated Compilation Videos
No recording needed. Fully automated.

```
# Combine multiple app screenshots with voiceover
# "5 Apps We Built at Black Layers"

1. Take 3-5 screenshots per app
2. Write narration for each app (30 seconds)
3. Generate voiceover with Edge-TTS
4. Add background music (royalty-free from Pixabay)
5. Combine with FFmpeg
6. Upload to YouTube
```

## Upload Process
```
1. Open browser to studio.youtube.com
2. Click "Create" → "Upload video"
3. Upload the generated video file
4. Fill in title, description, tags (from script)
5. Set thumbnail
6. Set visibility to "Public"
7. Click "Publish"
8. Send WhatsApp notification to Abdul: "New video uploaded: [title] [link]"
```

## Voice Settings
- Primary voice: `en-US-GuyNeural` (professional male)
- Alternative: `en-US-ChristopherNeural` (casual male)
- Speed: Normal (1.0x)
- Always add 0.5s pause between sentences
