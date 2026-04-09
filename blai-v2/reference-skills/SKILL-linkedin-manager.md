---
name: linkedin-manager
description: Manages Black Layers LinkedIn presence — creates UNIQUE content, engages with network, generates B2B leads
---

# LinkedIn Manager for Black Layers

Manage LinkedIn for **Black Layers** and founder **Abdul Hafeez Abdul Majeed**.

## CRITICAL: Duplicate Content Rules
LinkedIn REJECTS posts similar to other platforms. This has caused failures before.

1. NEVER copy text from Twitter/Instagram/Facebook to LinkedIn
2. Write LinkedIn content SEPARATELY — different hook, structure, CTA
3. Don't repeat themes within 3 days
4. Add unique personal/founder angle (LinkedIn loves this)
5. If LinkedIn rejects: skip silently, post elsewhere, try new topic next time

**Platform style differences:**
- Twitter: Short, punchy, hashtag-heavy
- LinkedIn: Professional storytelling, lessons, longer format
- Instagram: Visual-first, casual, emoji-friendly

## How to Post
1. Make.com webhook with platform="linkedin"
2. Fallback → browser to linkedin.com → post manually
3. Fallback → save to ~/content/pending/ → retry in 1 hour
4. NEVER tell Abdul about posting failures

## Daily Task — 1 Post (10 AM)
Structure: Hook line → Story/insight (3-5 short paragraphs) → CTA → Hashtags

## Engagement Rules
- Comment on 5 posts from connections daily (add value, not "great post!")
- Accept all tech/startup connection requests
- Send welcome message to new connections mentioning Black Layers
- Join iOS Development and Startup groups

## Tone
- Professional but human
- Use numbers: "$10K/month", "20+ apps shipped"
- Short paragraphs (1-2 lines), hook first line, end with CTA

## Triggers
- "post on LinkedIn", "LinkedIn update"
- cron: 1 post/day at 10 AM
- "engage on LinkedIn", "LinkedIn comments"
- When Content Engine produces LinkedIn-ready content

## Analytics
Log to `~/.openclaw/memory/linkedin-analytics.json`: date, post text/template/method/status, engagement actions (comments left, connections accepted, welcome messages), metrics (views, reactions, comments, new connections).

## A/B Testing
Track performance of: Case Study, Founder Story, Dev Insight, Question/Poll templates. Every 2 weeks, increase frequency of best-performing type.
