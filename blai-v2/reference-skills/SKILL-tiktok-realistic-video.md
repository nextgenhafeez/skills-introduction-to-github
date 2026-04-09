---
name: tiktok-realistic-video
description: Create realistic AI videos and post on TikTok
---

# TikTok Realistic AI Video Pipeline

## Video Generation Platforms
| Platform | URL | Free Tier |
|----------|-----|-----------|
| HaiLuo (best quality) | hailuoai.video | ~10 videos/day |
| Kling AI | klingai.com | ~66 credits/day |
| SiliconFlow (API) | siliconflow.cn | Free credits, access to Wan 2.1, CogVideoX |

## Generation Methods
- **HaiLuo Web**: Open hailuoai.video, enter prompt, download MP4 to ~/content/tiktok-video.mp4
- **MiniMax API**: POST to `https://api.minimax.chat/v1/video_generation` with model `video-01-live`, poll `query/video_generation?task_id=`
- **Wan 2.1 via SiliconFlow**: POST to `https://api.siliconflow.cn/v1/video/generations` with model `Wan-AI/Wan2.1-T2V-14B`, resolution 1080x1920

## Post-Production
- Add text overlay with ffmpeg drawtext filter
- Add voiceover with edge-tts (voice: en-US-AndrewNeural)
- Combine video + voiceover with ffmpeg

## Posting Methods
1. **Browser**: tiktok.com/upload → upload ~/content/tiktok-final.mp4
2. **Make.com webhook**: POST video + caption to webhook
3. **TikTok Developer API**: OAuth via developers.tiktok.com

## Cron: 2 posts/day
- `0 9 * * *` — morning post via ~/tiktok-video-gen.py
- `0 19 * * *` — evening post

## Prompt Library (pick best for context)
- **App showcase**: Cinematic slow-motion, iPhone 16 Pro, beautiful iOS app, soft blue rim lighting, shallow DOF, 4K
- **Dev workspace**: Tracking shot, MacBook Pro with Xcode, warm ambient lighting, cinematic
- **Viral hook**: Snap zoom into screen, code transforming into app, electric blue accents, high energy
- **Reveal**: Dramatic slow reveal, black to lit iPhone, camera pulling back, movie trailer style

## Execution Rules
1. On "make a TikTok video" → generate immediately
2. Fallback chain on failure: HaiLuo → Kling → Wan → CogVideo
3. Always add text overlay + voiceover before posting
4. Always vertical 1080x1920
5. Cross-post to YouTube Shorts + Instagram Reels
6. Never ask which prompt — pick best and generate
7. Send final video to Boss on WhatsApp immediately
8. Never explain — just DO IT
