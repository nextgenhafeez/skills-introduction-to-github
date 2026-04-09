# SKILL: Trend Tracker + AI Model Intelligence

## Purpose
Stay updated on internet trends, viral formats, and latest AI models. Use this to create timely content for Black Layers social media.

---

## Trending Content Formats (April 2026)

### TikTok/Reels Viral Formats
1. "If You Wanna Get With Me" brand intro (Altégo remix)
2. "Oh Ok Because" box step wordplay (Azealia Banks 212)
3. Color Hunting Challenge — photograph everything in one hue
4. Silent tutorials — hands + screen recording + text overlay + trending audio
5. "Day in the life" developer content
6. Split-screen hooks (before/after, problem/solution)
7. Build in public — real coding, real failures, real results

### Viral Hooks for Tech/Dev
- "POV: AI agent runs your business", "Built this app in 24h with AI", "My AI agent did THIS while I slept", "Stop building apps nobody asked for"

### Top Hashtags
#BuildInPublic #TechTok #AITools #AppDev #iOSDeveloper #CodingLife #StartupLife #AIAgent #SwiftUI #IndieHacker #AIAutomation #Kling #AIVideo

### Posting Schedule
- Morning 9AM: educational/tips
- Evening 7PM: showcase/results/demos
- Weekend: behind-scenes, personal brand, week review

---

## AI Models Rankings (April 2026)

### Video Generation
1. **Google Veo 3.1** — physical realism + native audio (Vertex AI, pay-per-use)
2. **Kling 3.0** — multi-shot, up to 2min (66 free credits/day, $6.99-$180/mo)
3. **Runway Gen-4.5** — cinematic, narrative continuity ($15-$95/mo)
4. **Sora 2** — via ChatGPT only (standalone shut down), 25s max ($20-$200/mo)
5. **Luma Ray3** — fast, good quality (free tier)
6. **Wan 2.2** — open-source, self-hostable (free)
7. **HaiLuo/MiniMax Video-01-Live** — best free quality (~10 free/day, api.minimax.chat)

### Image Generation
1. **Midjourney V8** — aesthetics, 5x faster, native 2K (no free tier)
2. **Flux 2 Pro/Flex** — photorealism (Replicate/fal.ai, Schnell=free)
3. **GPT Image 1.5** — replaced DALL-E 3, 4x faster (OpenAI API, free via ChatGPT)
4. **Google Imagen 3** — photorealism + text (Vertex AI)
5. **Recraft V4** — #1 for logos, SVG export (free tier)
6. **Stable Diffusion 3.5** — open-source, local (free)

### Voice/TTS
1. **Fish Audio (Open Audio S1)** — #1 TTS-Arena, 4B model (open source)
2. **Voxtral TTS (Mistral)** — beats ElevenLabs, 3s voice cloning (FREE open source)
3. **Qwen3-TTS** — 10 languages, voice cloning (free open source)
4. **Chatterbox (Resemble AI)** — 63.8% preferred over ElevenLabs (open source)
5. **ElevenLabs** — industry standard (free tier limited)
6. **Edge-TTS (Microsoft)** — zero cost, no API key

**Upgrade recommendation:** Replace Edge-TTS with Voxtral TTS (free, better quality, 3s voice cloning).

### Content Tools
CapCut (auto-captions, free), Canva AI (social graphics, free tier), Opus Clip (long→short, free tier), Recraft V4 (#1 logos)

---

## Recommended Upgrades for BLAI
1. **TTS**: Edge-TTS → Voxtral TTS (free, open source, voice cloning)
2. **Backup video**: Add HaiLuo/MiniMax as Kling backup (10 free/day, api.minimax.chat)
3. **Image gen**: Flux 2 Schnell (free) via Replicate/fal.ai for thumbnails
4. **Logos**: Recraft V4 for brand assets

---

## Content Ideas for Black Layers
1. "My AI agent handles clients while I sleep" — screen record BLAI
2. "iOS app in 60 seconds" — SwiftUI speed-build
3. "I replaced my marketing team with AI" — show BLAI posting/responding
4. "What $0/month AI stack vs $200/month looks like"

## Trend Scanning Workflow
- Weekly Monday 6 AM: scan TikTok Creative Center (top hashtags), Twitter/X trending, Product Hunt launches, HuggingFace trending models
- Score trends by relevance (AI/app/dev/startup keywords + growth rate + freshness)
- Update this file's content sections with fresh data
- Notify Content Engine, Video Creator, Twitter Manager with new trends

## Rules
- Check trends WEEKLY — content gets stale fast
- Always use trending audio on TikTok
- Vertical 9:16 for TikTok/Reels/Shorts, square 1:1 for IG feed/LinkedIn, horizontal 16:9 for YouTube/website
- Post at peak hours: 9 AM and 7 PM (Boss's timezone)
- Track which posts perform best — double down on winners
- When new AI model drops, test immediately and post comparison

## Triggers
- cron: "0 6 * * 1" (weekly Monday 6 AM)
- "what's trending", "latest trends", "new AI models", "content ideas"
- When any content skill needs fresh ideas

## Storage
Trend history: ~/.openclaw/memory/trend-history.json (date, top_trends, new_models, ideas generated/used/viral)
