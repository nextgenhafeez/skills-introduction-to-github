# SKILL: Kling 3.0 Video Generator + Social Media Poster

## Purpose
Generate AI videos using Kling 3.0 API, post to TikTok/YouTube Shorts/Instagram Reels, deliver to Boss's Mac via SCP.

## Config
- API: https://api.klingai.com
- Auth: JWT (HS256) using KLING_ACCESS_KEY (AK) + KLING_SECRET_KEY (SK) from env
- Keys portal: https://app.klingai.com/global/dev
- Script: ~/scripts/kling-video.py
- Output dir: ~/content/videos
- Mac delivery: SCP to tonny@100.105.165.84:/Users/tonny/Downloads
- Dependencies: PyJWT, requests

## Free Tier
- 66 credits/day (resets daily, no rollover)
- 5s standard=10 credits (6 videos/day), 5s pro=35 credits (1 video/day)
- 10s standard=20 credits (3 videos/day), 10s pro=70 credits (need paid)
- Free: watermarked, max 5s, 720p. Pro plan ($25.99/mo): 3000 credits, no watermark, 1080p+

## API Endpoints
- Text-to-video: POST /v1/videos/text2video — body: model_name "kling-v3", prompt, negative_prompt, duration (3/5/10/15), aspect_ratio (16:9/9:16/1:1), mode (std/pro), cfg_scale (0.0-1.0)
- Image-to-video: POST /v1/videos/image2video — body: model_name "kling-v3", image (URL), prompt, negative_prompt, duration, aspect_ratio, mode
- Poll status: GET /v1/videos/{text2video|image2video}/{task_id} — poll every 8s, max 5min. Status: succeed → task_result.videos[0].url | failed → abort
- Auth header: Bearer {JWT_token}

## Usage
- Basic: `python3 ~/scripts/kling-video.py "prompt" --duration 5 --aspect 9:16 --deliver`
- Image-to-video: add `--image "https://..."` flag
- With voiceover: add `--voiceover "script text"` (uses edge-tts en-US-AndrewNeural + ffmpeg merge)
- Pro quality: `--mode pro`
- Custom name: `--name "bl_morning"`
- Skip delivery: `--no-deliver`

## Prompt Structure
`[SUBJECT] + [ACTION] + [ENVIRONMENT] + [LIGHTING] + [CAMERA] + [STYLE]`

Default negative prompt: "blurry, distorted faces, text artifacts, watermark, low quality, cartoon, anime, static, jittery, flickering"

## Post-Processing
- Branding overlay: ffmpeg overlay with ~/content/images/bl-watermark.png at bottom-right
- Text caption: ffmpeg drawtext centered near bottom
- Voiceover: edge-tts → ffmpeg merge audio+video

## Social Media Posting
- Option A (recommended): Make.com webhook — POST video+caption+platforms to webhook URL
- Option B: Direct platform API uploads (requires OAuth)
- Option C: SCP to Boss's Mac + WhatsApp caption notification

## Cron
- 9 AM UTC: `python3 kling-video.py "$(python3 daily-prompt.py morning)" --duration 5 --aspect 9:16 --voiceover "$(python3 daily-script.py morning)" --deliver --name "bl_morning"`
- 7 PM UTC: same with "evening" parameter

## Rules
- ALWAYS 9:16 for TikTok/Reels/Shorts, 16:9 for YouTube/LinkedIn
- ALWAYS include negative prompt
- ALWAYS deliver to Boss's Mac after generation
- NEVER exceed daily credit budget — track usage
- Prompt max: 2500 chars
- Download immediately — Kling deletes after 30 days
- Rate limit: wait 60s and retry once
- Task fail: reduce duration or switch to std mode
- Budget strategy (free tier): use standard 5s clips, 2-3/day. Save pro for important posts.
