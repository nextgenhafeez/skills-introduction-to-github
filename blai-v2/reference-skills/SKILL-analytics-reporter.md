---
name: analytics-reporter
description: Tracks performance across all platforms, analyzes engagement, sends daily/weekly reports to Abdul via WhatsApp
---

# Analytics Reporter for Black Layers

## Daily Report — WhatsApp at 8 PM
Cover: Twitter (tweets, impressions, likes, followers, best tweet) | LinkedIn (posts, views, reactions, connections) | Instagram (posts, likes, followers) | Other (Quora answers, Reddit, website visitors) | Leads (new inquiries, hot leads) | Top content today + tomorrow's plan

## Weekly Report — WhatsApp every Friday 6 PM
Cover: Growth per platform (start→end followers) | Content published counts per platform | Top 3 posts with engagement | What worked & didn't | Leads generated + revenue potential | Next week strategy adjustments

## Data Collection
- **Twitter**: analytics.twitter.com or API v2 (`/2/users/{user_id}/tweets` with `tweet.fields=public_metrics`)
- **LinkedIn**: linkedin.com/analytics via browser (no free API)
- **Instagram**: instagram.com Insights or business.facebook.com
- **YouTube**: studio.youtube.com Analytics tab
- **Automated**: `~/.openclaw/scripts/collect-analytics.py` aggregates all platform logs at 7:30 PM

## Data Storage
Save to `~/.openclaw/memory/engagement-data.json` keyed by date with per-platform metrics (followers, impressions, likes, views, reactions, subscribers) + leads count + top_post.

## Auto-Adjustment Rules
Based on data, automatically adjust: posting times → highest engagement windows | content types → more of what gets likes/comments | hashtags → highest impression drivers | platform focus → fastest-growing | topics → highest engagement

## Triggers
- cron: `0 20 * * *` (daily 8 PM), `0 18 * * 5` (weekly Friday 6 PM)
- "how are we doing", "show me analytics", "engagement report", "performance update"

## Trend Detection
Flag: follower spike (+10% day-over-day), zero engagement on published content, performance drop (30% below last week).

## Delivery Fallback
1. WhatsApp (primary) → 2. Save to `~/reports/daily/YYYY-MM-DD.txt` → 3. File-delivery skill
