---
name: image-creator
description: Creates social media graphics, thumbnails, quote cards, and infographics for Black Layers
---

# Image Creator for Black Layers

## Tools
- **Canva** (browser): Professional templates
- **ImageMagick** (CLI): Quick text-based graphics
- **Browser screenshots**: App pages, code snippets (carbon.now.sh, theme "One Dark")

## Brand Guidelines
Colors: Black #000, White #FFF, Accent Blue #2563EB | Font: Clean sans-serif (Inter, Helvetica, SF Pro) | Style: Minimal, dark theme, high contrast | Logo: BL mark white on dark

## Image Sizes
| Platform | Post | Story/Reel | Header |
|----------|------|------------|--------|
| Twitter | 1200x675 | — | 1500x500 |
| LinkedIn | 1200x627 | — | 1584x396 |
| Instagram | 1080x1080 | 1080x1920 | — |
| YouTube Thumb | 1280x720 | 1080x1920 (Short) | 2560x1440 |

## Image Types
1. **Quote cards** — Dark bg, white text, BL logo
2. **App showcase** — Screenshot + description overlay (via Canva)
3. **Code snippets** — carbon.now.sh, One Dark theme
4. **Before/After** — Wireframe vs final (Instagram carousel)
5. **Stats/Infographic** — "$10K+/mo", "20+ apps", "5-star reviews"
6. **YouTube thumbnails** — Bold text (3-5 words), app screenshot, dark bg + blue accent

## Daily Schedule
Mon: Quote card + blog header (Twitter+Medium) | Tue: App showcase (LinkedIn+Instagram) | Wed: Code snippet (Twitter) | Thu: Stats infographic (LinkedIn) | Fri: YouTube thumbnail

## Storage
`~/.openclaw/content/images/YYYY-MM-DD_platform_type.png`

## Fallback Chain
1. Flux 2 Schnell (Replicate) — free tier
2. Recraft V4 API — best for logos/brand assets
3. ImageMagick CLI — always available
4. Canva browser — last resort (slow)

## Triggers
- "create an image", "make a graphic", "design a post", "thumbnail for", "quote card for"
- Daily schedule triggers
