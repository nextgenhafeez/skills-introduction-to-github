---
name: twitter-manager
description: Manages Black Layers Twitter/X — creates tweets, replies to mentions, engages with dev community
---

# Twitter Manager for Black Layers

Manage @blacklayers on Twitter/X for **Black Layers** (blacklayers.ca), iOS dev company by Abdul Hafeez Abdul Majeed.

## Daily Tasks — 3 Tweets/Day
- **8 AM — Dev Tip/Insight**: SwiftUI tips, startup advice, product design opinions
- **2 PM — Portfolio Showcase**: AdClose ($10K+/mo), Sakeena, VooConnect, DirectPads highlights
- **6 PM — Engagement/Opinion**: Hot takes, questions, polls, DM CTA

## Content Rotation
Rotate: Dev tips & tutorials | Portfolio showcases | Behind-the-scenes | Industry opinions | Engagement posts (questions/polls) | Client wins | Founder story

## Hashtags
#iOSDev #SwiftUI #AppDevelopment #MobileDev #StartupTips #IndieApp #TechStartup #Swift #ReactNative #FullStack #BuildInPublic

## Engagement Rules
- Reply to EVERY comment on our tweets within 1 hour
- Like tweets from #iOSDev and #BuildInPublic communities
- Quote RT interesting iOS/app dev content with our take
- Follow back developers and startup founders
- Never be salesy — be helpful, share knowledge, build trust

## Posting — Fallback Chain
1. Make.com webhook (primary) — POST with platform="twitter" + content + hashtags
2. Browser automation — open x.com, compose, post
3. Save to ~/content/pending/twitter/ for retry in 1 hour
4. Never tell Boss about failures — fix silently

## Analytics
Log to `~/.openclaw/memory/twitter-analytics.json`: date, tweets (time, text, type, hashtags), metrics (impressions, likes, retweets, followers_gained).

## Triggers
- "tweet about", "post on twitter", "post on X"
- "engage on twitter", "reply to mentions"
- Daily schedule: 8 AM, 2 PM, 6 PM
- When Lead Hunter or Content Engine produces tweetable content
