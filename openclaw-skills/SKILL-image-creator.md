---
name: image-creator
description: Creates social media graphics, thumbnails, quote cards, and infographics for Black Layers using Canva browser automation and ImageMagick
---

# Image Creator for Black Layers

You create visual content for all Black Layers social media platforms.

## Tools Available
- **Canva** (via browser): Professional templates, drag-and-drop
- **ImageMagick** (CLI): Quick text-based graphics
- **Browser screenshots**: Capture app pages, code snippets

## Brand Guidelines

| Element | Value |
|---------|-------|
| Primary Color | Black (#000000) |
| Secondary Color | White (#FFFFFF) |
| Accent Color | Blue (#2563EB) |
| Font | Clean sans-serif (Inter, Helvetica, SF Pro) |
| Style | Minimal, dark theme, high contrast |
| Logo | BL mark (white on dark) |

## Image Sizes by Platform

| Platform | Post Size | Story/Reel | Header |
|----------|----------|------------|--------|
| Twitter | 1200 x 675 | — | 1500 x 500 |
| LinkedIn | 1200 x 627 | — | 1584 x 396 |
| Instagram | 1080 x 1080 | 1080 x 1920 | — |
| YouTube | — | 1080 x 1920 (Short) | 2560 x 1440 |
| YouTube Thumb | 1280 x 720 | — | — |

## Image Types to Create

### 1. Quote Cards (Twitter, LinkedIn, Instagram)
Dark background with white text. Include BL logo.

```bash
# ImageMagick quick quote card
convert -size 1200x675 xc:'#0a0a0a' \
  -font Helvetica-Bold -pointsize 40 -fill white \
  -gravity center -annotate 0 "The best apps solve\none problem really well." \
  -font Helvetica -pointsize 20 -fill '#2563EB' \
  -gravity south -annotate +0+40 "— Abdul Hafeez | blacklayers.ca" \
  quote-card.png
```

### 2. App Showcase (All Platforms)
Screenshot of app with description overlay.

**Process using Canva (browser):**
1. Open canva.com
2. Create new design (platform-specific size)
3. Set dark background
4. Upload app screenshot
5. Add title, description, BL logo
6. Download as PNG

### 3. Code Snippets (Twitter, LinkedIn)
Beautiful code screenshots for dev tips.

**Process:**
1. Open browser to carbon.now.sh
2. Paste code snippet
3. Set theme to "One Dark" (matches brand)
4. Set language (Swift/TypeScript/Python)
5. Export as PNG
6. Post with explanation caption

### 4. Before/After (Instagram Carousel)
Show app transformation — wireframe vs final product.

### 5. Stats/Infographic (LinkedIn, Twitter)
Numbers and achievements in visual format.
- "$10K+/month revenue"
- "20+ apps shipped"
- "5-star Fiverr reviews"
- "30-day delivery"

### 6. YouTube Thumbnails
High contrast, face + text + result.
- Bold text (3-5 words max)
- App screenshot or result number
- Dark background with blue accent

## Daily Image Tasks

| Day | Create | For |
|-----|--------|-----|
| Mon | Quote card + blog header | Twitter + Medium |
| Tue | App showcase graphic | LinkedIn + Instagram |
| Wed | Code snippet screenshot | Twitter |
| Thu | Stats infographic | LinkedIn |
| Fri | YouTube thumbnail | YouTube |

## File Storage
Save all created images to `~/.openclaw/content/images/` with naming:
```
YYYY-MM-DD_platform_type.png
Example: 2026-03-31_twitter_quote-card.png
```
