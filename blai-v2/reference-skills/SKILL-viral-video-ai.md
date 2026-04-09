---
name: viral-video-ai
description: Generate viral videos using free Chinese AI video generators + prompting for max views
---

# Viral AI Video Creation — Free Chinese Models

## AI Video Generators

| Model | Free Tier | API | Best For |
|-------|-----------|-----|----------|
| HaiLuo/MiniMax | ~10/day, no watermark | `POST https://api.minimax.chat/v1/video_generation` model: `video-01-live` | Cinematic |
| Kling AI | ~66 credits/day (~5-10 clips) | Replicate / FAL.ai | Realistic human motion |
| Wan 2.1 (Alibaba) | Unlimited (Apache 2.0) | DashScope, Replicate, SiliconFlow | Scale automation |
| CogVideoX (Zhipu) | Unlimited (open source, 2B/5B) | Self-host | Budget |
| HunyuanVideo (Tencent) | Unlimited (open source, 13B) | Self-host | Free quality |

URLs: hailuoai.video, klingai.com, HuggingFace: Wan-AI/Wan2.1-T2V-14B (or 1.3B for Mac GPU), GitHub: THUDM/CogVideo, Tencent/HunyuanVideo

## Prompting Formula
Structure: `[Camera movement], [subject], [action], [environment], [lighting], [style]`

Rules:
1. Front-load the visual hook — models weight the beginning more
2. Always specify camera movement: "dolly in", "orbital shot", "tracking shot"
3. Include lighting: "volumetric", "neon rim light", "golden hour"
4. Describe what viewer SEES, not metaphors
5. 30-80 words — too short = generic, too long = confused

## Algorithm Rules for Max Views
- **Hook** (first 0.5s): First frame must be arresting. Start mid-action, never title card. Text overlay: question > statement.
- **Length**: YouTube Shorts 15-30s, TikTok 7-15s, Reels 15-30s
- **Loop**: End connects visually to beginning — platforms reward re-watches
- **Posting**: 2-3x daily at peak hours (7-9am, 12-1pm, 7-10pm). Add TRENDING AUDIO. 3-5 hashtags (mix broad + niche). End with "Follow for more" or question.
- **Viral content types**: Satisfying transformation clips, tech "magic" visuals, before/after reveals, cinematic versions of dev tasks

## Automation Pipeline
- Model fallback chain: Kling → MiniMax → Wan 2.1
- Content dir: `~/.openclaw/content/videos`
- Post-process: FFmpeg adds "Black Layers" text overlay + trending audio
- Daily flow: Generate 3 clips (morning cron `0 7 * * *`) → FFmpeg overlay → upload to Shorts/TikTok/Reels → track analytics → feed winners back into prompts

## Triggers
- "make a viral video", "create short video", "generate reel", "TikTok content", "YouTube short", "Instagram reel"
- cron: "0 7 * * *" (morning batch)
- When Trend Tracker identifies a hot format
