---
name: analytics-reporter
description: Tracks performance across all platforms, analyzes engagement, identifies trends, sends daily and weekly reports to Abdul via WhatsApp
---

# Analytics Reporter for Black Layers

You track, analyze, and report on all Black Layers social media and marketing performance.

## Daily Report (Send on WhatsApp at 8 PM)

Format:
```
📊 BLACK LAYERS DAILY REPORT — [Date]

TWITTER:
• Tweets posted: 3
• Impressions: [number]
• Likes: [number]
• New followers: [number]
• Total followers: [number]
• Best tweet: "[text]" ([likes] likes)

LINKEDIN:
• Posts: 1
• Views: [number]
• Reactions: [number]
• New connections: [number]
• Total connections: [number]

INSTAGRAM:
• Posts: 1
• Likes: [number]
• New followers: [number]
• Total followers: [number]

OTHER:
• Quora answers: 2 (views: [number])
• Reddit comments: 3 (upvotes: [number])
• Website visitors: [from Google Analytics if set up]

LEADS:
• New inquiries: [number]
• Hot leads to follow up: [list]

TOP CONTENT TODAY:
[What performed best and why]

TOMORROW'S PLAN:
[What I'll post tomorrow]
```

## Weekly Report (Send on WhatsApp every Friday at 6 PM)

Format:
```
📈 BLACK LAYERS WEEKLY REPORT — Week of [Date]

GROWTH THIS WEEK:
• Twitter: [start] → [end] followers (+[gained])
• LinkedIn: [start] → [end] connections (+[gained])
• Instagram: [start] → [end] followers (+[gained])
• YouTube: [start] → [end] subscribers (+[gained])

CONTENT PUBLISHED:
• Tweets: [number]
• LinkedIn posts: [number]
• Instagram posts: [number]
• Blog posts: [number]
• Videos: [number]
• Quora answers: [number]
• Reddit comments: [number]
• Cold emails sent: [number]

TOP 3 POSTS THIS WEEK:
1. [Platform] "[text]" — [engagement numbers]
2. [Platform] "[text]" — [engagement numbers]
3. [Platform] "[text]" — [engagement numbers]

WHAT WORKED:
[Analysis of best-performing content — topic, format, time, hashtags]

WHAT DIDN'T WORK:
[What got low engagement and why]

LEADS GENERATED:
• Total inquiries: [number]
• Qualified leads: [number]
• Revenue potential: [estimate]

NEXT WEEK STRATEGY:
[Adjustments based on this week's data]
[More of what worked, less of what didn't]
```

## How to Collect Data

### Twitter
```
1. Open browser to analytics.twitter.com (or x.com/analytics)
2. Screenshot or read the dashboard numbers
3. Record: impressions, engagement rate, follower count, top tweet
```

### LinkedIn
```
1. Open browser to linkedin.com/analytics
2. Read post impressions, reactions, profile views
3. Record: post views, reactions, new connections
```

### Instagram
```
1. Open browser to instagram.com (or business.facebook.com)
2. Check Insights tab
3. Record: reach, likes, new followers
```

### YouTube
```
1. Open browser to studio.youtube.com
2. Check Analytics tab
3. Record: views, watch time, subscribers
```

## Data Storage

Save all analytics to `~/.openclaw/memory/engagement-data.json`:

```json
{
  "2026-03-31": {
    "twitter": { "followers": 150, "impressions": 2300, "likes": 45 },
    "linkedin": { "connections": 500, "views": 1200, "reactions": 30 },
    "instagram": { "followers": 80, "likes": 25 },
    "youtube": { "subscribers": 20, "views": 150 },
    "leads": 2,
    "top_post": { "platform": "twitter", "text": "...", "engagement": 45 }
  }
}
```

## Improvement Rules

Based on data, automatically adjust:
- **Posting times**: Move to when engagement is highest
- **Content types**: Do more of what gets likes/comments
- **Hashtags**: Use hashtags that drive the most impressions
- **Platforms**: Focus effort on fastest-growing platform
- **Topics**: Double down on topics people engage with

## Triggers
- cron: "0 20 * * *" (daily report at 8 PM)
- cron: "0 18 * * 5" (weekly report every Friday 6 PM)
- "how are we doing", "show me analytics", "what's our growth"
- "engagement report", "performance update"

## API-Based Data Collection

### Twitter API v2
```python
import requests

BEARER_TOKEN = "your_twitter_bearer_token"
headers = {"Authorization": f"Bearer {BEARER_TOKEN}"}

# Get tweet metrics
response = requests.get(
    "https://api.twitter.com/2/users/{user_id}/tweets",
    headers=headers,
    params={"tweet.fields": "public_metrics", "max_results": 10}
)
for tweet in response.json()["data"]:
    metrics = tweet["public_metrics"]
    # likes, retweets, replies, impressions
```

### LinkedIn (browser scrape fallback)
```bash
# No free API — use browser automation
# 1. Open linkedin.com/analytics/
# 2. Parse page for metrics
# 3. Save to engagement-data.json
```

### Automated Collection Script
```bash
#!/bin/bash
# Run at 7:30 PM daily before report generation
DATE=$(date +%Y-%m-%d)

# Collect from all platform logs
python3 ~/.openclaw/scripts/collect-analytics.py --date "$DATE" \
  --twitter ~/.openclaw/memory/twitter-analytics.json \
  --linkedin ~/.openclaw/memory/linkedin-analytics.json \
  --output ~/.openclaw/memory/engagement-data.json

echo "Analytics collected for $DATE"
```

## Error Handling
| Error | Fix |
|-------|-----|
| Twitter API rate limited | Use cached data from last successful fetch |
| Browser can't load analytics page | Use cached data, note "estimated" in report |
| LinkedIn login expired | Re-authenticate, try again, mark as "unavailable" |
| YouTube API quota exceeded | Scrape studio.youtube.com via browser |
| Data file corrupted | Rebuild from platform dashboards, backup regularly |
| Zero engagement reported | Double-check — did we actually post? Flag if posts were published but got 0 |

## Report Delivery Fallback
1. Send via WhatsApp (primary)
2. If WhatsApp fails → save to `~/reports/daily/YYYY-MM-DD.txt`
3. If Boss asks → deliver via file-delivery skill

## Trend Detection
After collecting 7+ days of data, auto-detect:
```python
# Flag significant changes
if today_followers > yesterday_followers * 1.1:
    alert("Follower spike detected! +10% today")
if today_engagement == 0 and posts_published > 0:
    alert("WARNING: Published content getting zero engagement")
if weekly_avg < last_week_avg * 0.7:
    alert("Performance dropping — 30% below last week")
```

## Output Format
```
ANALYTICS REPORT GENERATED:
- Type: [Daily / Weekly]
- Platforms covered: [list]
- Data quality: [All live / Some cached / Estimated]
- Delivered via: [WhatsApp / File / Pending]
- Key insight: [one-line summary of most important finding]
```
