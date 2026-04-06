# SKILL: Trend Tracker + AI Model Intelligence

## Purpose
Stay updated on internet trends, viral content formats, and latest AI models. Use this knowledge to create timely, relevant content for Black Layers social media.

---

## PART 1: TRENDING CONTENT (April 2026)

### TikTok/Reels Viral Formats Right Now
1. **"If You Wanna Get With Me" brand intro** — Altégo remix of Dev's "Bass Down Low" — creators use it to introduce their brand/service with a confident walk-in
2. **"Oh Ok Because" box step wordplay** — Azealia Banks' "212" instrumental — quick-fire listing of achievements/skills
3. **Color Hunting Challenge** — assign yourself a color, photograph everything in that hue, reveal an aesthetic collage grid
4. **Silent tutorials** — no talking, just hands + screen recording + text overlay + trending audio
5. **"Day in the life" of developers** — behind-the-scenes dev work, relatable moments
6. **Split-screen hooks** — before/after, problem/solution format
7. **Build in public** — show real coding, real failures, real results

### Viral Content Hooks for Tech/Dev
- "POV: You hire an AI agent to run your business"
- "I built this app in 24 hours using AI"
- "What $500/month gets you in cloud computing"
- "Stop building apps nobody asked for"
- "My AI agent just did THIS while I was sleeping"
- "The app idea that made me $X"

### Top Performing Hashtags (Tech/AI)
```
#BuildInPublic #TechTok #AITools #AppDev #iOSDeveloper
#LearnOnTikTok #CodingLife #StartupLife #AIAgent #NoCode
#SwiftUI #IndieHacker #SaaS #DevLife #AIAutomation
#Kling #AIVideo #ContentCreator #DigitalAgency
```

### Content Calendar Strategy
- **Morning post (9 AM)**: Educational/tip content — "How to..." or "Did you know..."
- **Evening post (7 PM)**: Showcase/results — app demos, AI agent demos, before/after
- **Weekend**: Behind-the-scenes, personal brand, "week in review"

---

## PART 2: LATEST AI MODELS (April 2026)

### VIDEO GENERATION — Current Rankings

| Rank | Model | Version | Best For | API | Free Tier | Price |
|------|-------|---------|----------|-----|-----------|-------|
| 1 | **Google Veo** | 3.1 | Physical realism + native audio | Vertex AI | Limited | Pay-per-use |
| 2 | **Kling** | 3.0 | Multi-shot sequences, long clips (up to 2 min) | api.klingai.com | 66 credits/day | $6.99-$180/mo |
| 3 | **Runway** | Gen-4.5 | Cinematic quality, narrative continuity | Yes | Free credits | $15-$95/mo |
| 4 | **Sora** | 2 (in ChatGPT) | Cinematic quality, realistic physics | Via ChatGPT | No (Plus $20/mo) | $20-$200/mo |
| 5 | **Luma** | Ray3 | Fast generation, good quality | Yes | Free tier | Varies |
| 6 | **Wan** | 2.2 | Open-source, self-hostable | Open source | Free | Free |
| 7 | **Pika** | 2.x | Fun effects, lip sync | Limited | Free tier | Varies |
| 8 | **HaiLuo/MiniMax** | Video-01-Live | Best free quality | api.minimax.chat | ~10 free/day | Free-$30/mo |

**Key news:** Sora standalone app was SHUT DOWN. Video generation only via ChatGPT now. Kling 3.0 can generate up to 2 minutes vs Sora's 25 seconds.

### IMAGE GENERATION — Current Rankings

| Rank | Model | Version | Best For | API | Free Tier |
|------|-------|---------|----------|-----|-----------|
| 1 | **Midjourney** | V8 | Aesthetics, artistic quality (5x faster, native 2K) | Discord/Web | No |
| 2 | **Flux** | 2 Pro/Flex | Photorealism, camera-accurate | Replicate, fal.ai | Flux Schnell free |
| 3 | **GPT Image** | 1.5 | Replaced DALL-E 3, 4x faster photorealism | OpenAI API | Via ChatGPT free |
| 4 | **Google Imagen** | 3 | Photorealism + text rendering | Vertex AI | Limited |
| 5 | **Recraft** | V4 | Logos, SVG export, brand styling | Yes | Free tier |
| 6 | **Ideogram** | 2.0+ | Text in images | Yes | Free tier |
| 7 | **Leonardo** | Phoenix | Creative, stylized | Yes | Free daily credits |
| 8 | **Stable Diffusion** | 3.5 | Open-source, local | Open source | Free |

**Key news:** DALL-E 3 is REPLACED by GPT Image 1.5. Midjourney V8 launched with completely rewritten engine. Recraft V4 is #1 for logos on HuggingFace.

### VOICE/TTS — Current Rankings

| Rank | Model | Key Feature | Free? | API |
|------|-------|-------------|-------|-----|
| 1 | **Fish Audio (Open Audio S1)** | #1 on TTS-Arena, 4B model | Open source | Yes |
| 2 | **Voxtral TTS (Mistral)** | Beats ElevenLabs in blind tests, 3s voice cloning | FREE open source | Yes |
| 3 | **Qwen3-TTS** | 10 languages, voice cloning, 0.6B/1.7B sizes | FREE open source | Yes |
| 4 | **Chatterbox (Resemble AI)** | 63.8% preferred over ElevenLabs, 5-10s cloning | Open source | Yes |
| 5 | **ElevenLabs** | Industry standard, best ecosystem | Free tier (limited) | Yes |
| 6 | **Edge-TTS (Microsoft)** | Zero cost, no API key needed | FREE | N/A |
| 7 | **Bark** | Speech + laughter + music + environmental sounds | Open source | Yes |
| 8 | **Coqui XTTS** | v2.5, 6-second voice cloning | Open source | Yes |

**Key news:** Voxtral TTS from Mistral beats ElevenLabs and is FREE. Fish Audio's Open Audio S1 is #1 on TTS-Arena. Consider upgrading from Edge-TTS to Voxtral or Fish Audio.

### AI CONTENT TOOLS — Top Picks 2026

| Tool | Best For | Free? |
|------|----------|-------|
| **CapCut** | Auto-captions, AI editing, effects | Yes |
| **Canva AI** | Social graphics, carousels, Magic Design | Free tier |
| **Opus Clip** | Long video → short clips | Free tier |
| **Descript** | AI video/audio editing | Free tier |
| **PostEverywhere** | All-in-one social posting | Free tier |
| **Adobe Firefly** | Copyright-safe image generation | Free tier |

---

## PART 3: RECOMMENDED UPGRADE PATH FOR BLAI

### Priority 1: Upgrade TTS (Free)
Replace Edge-TTS with **Voxtral TTS** (Mistral) — better quality, free, open source:
```bash
# Install on VM
pip install voxtral  # or clone from HuggingFace
# 3-second voice cloning — record Boss's voice once, use forever
```

### Priority 2: Add Backup Video APIs (Free)
Add **HaiLuo/MiniMax** as Kling backup (10 free videos/day):
```bash
export MINIMAX_API_KEY="your_key"
# API: api.minimax.chat/v1/video_generation
```

### Priority 3: Add Image Generation
Use **Flux 2 Schnell** (free) via Replicate for thumbnails and social posts:
```bash
# Via Replicate API or fal.ai — free tier available
```

### Priority 4: Use Recraft V4 for Logos
When Boss needs logo variations or brand assets — Recraft V4 is #1 for this.

---

## PART 4: CONTENT IDEAS FOR BLACK LAYERS (April 2026)

### This Week's Video Ideas
1. **"My AI agent handles my clients while I sleep"** — screen record BLAI processing orders/messages
2. **"iOS app in 60 seconds"** — speed-build an app feature in SwiftUI, satisfying code compilation
3. **"I replaced my entire marketing team with AI"** — show BLAI posting, creating content, responding
4. **"The truth about AI app development agencies"** — hot take, developer POV
5. **"What $0/month AI stack looks like vs $200/month"** — compare free tools vs paid

### Prompt Templates for Kling Videos
```
# App Showcase
"Close-up of hands holding iPhone 15 Pro, scrolling through a [TYPE] app, dark UI with [COLOR] accents, shallow depth of field, warm studio lighting, cinematic 4K"

# Developer at Work
"Medium shot developer coding [LANGUAGE] on MacBook Pro, modern dark office, multiple monitors, [COLOR] ambient lighting, camera slowly dollies in, documentary style"

# AI Agent Demo
"Split screen: WhatsApp chat on left with messages auto-appearing, server terminal on right processing requests, dark theme, green text, tech documentary"

# Brand Reveal
"Elegant 3D text '[BRAND NAME]' materializing from dark particles, black and white, minimal, camera orbits, premium corporate"
```

---

## Rules
- Check trends WEEKLY — content gets stale fast
- Always use trending audio on TikTok posts
- Use vertical (9:16) for TikTok/Reels/Shorts
- Use square (1:1) for Instagram feed, LinkedIn
- Use horizontal (16:9) for YouTube, website
- Post at peak hours: 9 AM and 7 PM (Boss's timezone)
- Track which posts perform best — double down on winners
- When a new AI model drops, test it immediately and post a comparison video

## Triggers
- cron: "0 6 * * 1" (weekly scan every Monday 6 AM)
- "what's trending", "latest trends", "new AI models"
- "content ideas", "what should I post about"
- When any content skill needs fresh ideas or prompts

## Automated Trend Scanning Workflow

### Step 1: Scan Sources (browser automation)
```bash
#!/bin/bash
# Weekly trend scan — run Monday 6 AM
DATE=$(date +%Y-%m-%d)

# Scan TikTok trending
echo "Scanning TikTok Creative Center..."
# Browser: open https://ads.tiktok.com/business/creativecenter/inspiration/popular/hashtag/
# Extract top 10 hashtags in tech/business category

# Scan Twitter trending
echo "Scanning X/Twitter trends..."
# Browser: open https://x.com/explore/tabs/trending
# Extract tech-related trends

# Scan Product Hunt
echo "Scanning Product Hunt launches..."
# Browser: open https://www.producthunt.com
# Note top AI/dev tools launched this week

# Scan HuggingFace
echo "Scanning HuggingFace for new models..."
# Browser: open https://huggingface.co/models?sort=trending
# Note any new video/image/voice models
```

### Step 2: Analyze & Score Trends
```python
def score_trend(trend):
    """Score trend relevance for Black Layers content."""
    score = 0
    relevant_keywords = ["ai", "app", "developer", "startup", "ios", "coding", "tech", "saas"]
    for kw in relevant_keywords:
        if kw in trend["name"].lower():
            score += 20
    if trend["growth_rate"] > 50:  # % growth
        score += 30
    if trend["age_days"] < 3:  # fresh trend
        score += 20
    return score
```

### Step 3: Update This File
After scanning, update PART 1 (Trending Content) and PART 2 (AI Models) with fresh data.

### Step 4: Push to Content Skills
Notify Content Engine, Video Creator, and Twitter Manager about new trends:
```json
{
  "date": "2026-04-05",
  "trends": [
    {"name": "trend name", "platform": "tiktok", "relevance": 80, "content_idea": "..."}
  ],
  "new_models": [
    {"name": "model", "type": "video", "improvement": "2x faster than previous"}
  ],
  "recommended_hashtags": ["#AIAgent", "#BuildInPublic"],
  "audio_trending": ["song name — artist"]
}
```

## Error Handling
| Error | Fix |
|-------|-----|
| TikTok Creative Center blocked | Use VPN or scrape via API alternative |
| Browser timeout on trend pages | Retry with fresh session, reduce page load |
| HuggingFace rate limited | Use cached model list, update next day |
| Trend data is stale (>7 days old) | Force rescan, flag content as "unverified trend" |
| Can't determine trend relevance | Default to safe content themes, skip risky trends |

## Trend History
Store all scans in `~/.openclaw/memory/trend-history.json` for pattern analysis:
```json
{
  "scans": [
    {
      "date": "2026-04-05",
      "top_trends": ["trend1", "trend2"],
      "new_models": ["model1"],
      "content_ideas_generated": 5,
      "ideas_used": 3,
      "ideas_viral": 1
    }
  ]
}
```

## Output Format
```
TREND SCAN COMPLETE:
- Sources scanned: [list]
- New trends found: [count]
- New AI models: [count]
- Content ideas generated: [count]
- Skills notified: [Content Engine, Video Creator, etc.]
- Next scan: [date]
```
