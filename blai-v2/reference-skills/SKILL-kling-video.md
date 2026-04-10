# SKILL: Kling AI Video Generation (REAL)

## What this skill does
Generate real videos from text prompts or animate still images into dynamic
videos via the Kling AI API. This is an executable skill — when Boss asks to
"make a video" or "animate this image", the skill_router calls
`skills.kling_video.generate_and_wait()` which talks to `api.klingai.com`,
polls until done, downloads the mp4, and returns the real file path.

## Two modes — pick the RIGHT one

### 1. text_to_video (mode: "text2video")
Use when Boss gives only a text description.
Examples:
- "generate a video of a luxury iPhone app launch in a dark studio"
- "create a 5s reel about iOS developer life"
- "make a video showing a sleek dashboard animation"

### 2. image_to_video (mode: "image2video") — USE THIS FOR 3D IMAGES & DYNAMIC IMAGES
Use when Boss provides an image, logo, 3D render, product shot, or any still
picture that he wants "animated", "brought to life", or "made dynamic".
Examples of phrases that mean image2video:
- "animate this 3D model"
- "make this logo dynamic"
- "bring this render to life"
- "add motion to this image"
- "animate this product shot"
- "turn this static image into a video"

When Boss sends an image on WhatsApp along with the request, the image gets
saved to a tmp path and that path is passed as the `image=` argument.

## Parameters
- `prompt` (string, max 2500 chars) — what should happen in the video
- `negative_prompt` (string) — what to avoid. Always include at minimum:
  "blurry, low quality, distorted, watermark, text"
- `aspect_ratio` — "9:16" for TikTok/Reels/Shorts/Instagram, "16:9" for
  YouTube/LinkedIn/website. DEFAULT 9:16 unless Boss specifies YouTube.
- `duration` — 5 or 10 seconds. Start with 5 to conserve credits.
- `mode` — "std" (standard, cheaper, faster) or "pro" (higher quality,
  more credits). Default "std". Only use "pro" for important client/brand work.
- `image` — required only for image2video. May be an https URL or a local
  file path under /tmp/ or the BLAI workspace.

## Output
`generate_and_wait()` returns a plain-text summary like:
```
Video generated successfully.
  task_id: <id>
  prompt: <first 180 chars>
  aspect: 9:16, duration: 5s, mode: std
  saved to: /home/tonny/blai-v2/memory/videos/20260410_043015_abc12345.mp4
  size: 2145632 bytes
  source URL (expires ~30 days): https://...
```

The saved mp4 path is real. BLAI can quote it to Boss, send it to him via
WhatsApp, or hand it off to the social_poster_real skill for publishing.

## Rules (ABSOLUTE — never break)
1. NEVER claim a video was generated unless the skill actually returned
   "Video generated successfully." If the skill returns an error string,
   quote that error verbatim to Boss. Do NOT invent a fake task_id, fake
   file path, or fake success.
2. ALWAYS include a negative_prompt.
3. ALWAYS use 9:16 for short-form social (TikTok, Reels, Shorts, Instagram).
4. ALWAYS use 16:9 for long-form (YouTube, LinkedIn video, landing pages).
5. Downloads land in `memory/videos/`. The path is the source of truth —
   never fabricate a filename.
6. On failure: reduce duration from 10 to 5, or switch `mode` from "pro"
   to "std", then retry ONCE. If it still fails, report the real error to
   Boss and stop — do not retry in a loop.
7. Rate limit: if you see HTTP 429 or "rate limit" in the error, wait
   60 seconds and retry once.

## Credits / budget
Kling AI free tier is limited. Be conservative:
- Daily cap (self-imposed): 3 videos per day unless Boss says otherwise
- Prefer `mode="std"` over `mode="pro"`
- Prefer `duration=5` over `duration=10`
- Track usage with `list_recent_tasks()` — this reads from
  `memory/kling_log.json` which is updated on every real API call.

## Posting the video
After a video is generated, Boss may ask "post it to TikTok" or "post to
Instagram". That is handled by a DIFFERENT skill
(`social_poster_real.generate_and_post`) via Make.com webhooks. The Kling
skill only produces the file — it does not post.
