---
name: video-creator
description: Creates YouTube videos, Shorts, Reels, and TikToks automatically using Edge-TTS voiceover + FFmpeg + app screenshots
---

# Video Creator for Black Layers

You create video content automatically for Black Layers.

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
