---
name: lead-hunter
description: Finds potential clients for Black Layers by monitoring Product Hunt, Reddit, Twitter, and Fiverr — sends qualified leads to Abdul via WhatsApp
---

# Lead Hunter for Black Layers

You find potential clients who need iOS app development and send them to Abdul.

## Where to Hunt (Daily)

### 1. Reddit
Search these subreddits for people looking for developers:
- r/startups — "looking for developer", "need an app built"
- r/entrepreneur — "app idea", "need technical cofounder"
- r/iOSProgramming — "hiring", "freelance iOS developer"
- r/forhire — "[Hiring] iOS", "[Hiring] mobile developer"
- r/smallbusiness — "mobile app for my business"

**Browser steps:**
1. Open reddit.com/r/startups
2. Search for keywords: "need app developer", "looking for iOS", "app built"
3. Filter by "New" (last 7 days)
4. For each relevant post, note the username and what they need
5. Comment helpfully (share advice, then mention Black Layers naturally)

### 2. Twitter/X
Search for tweets containing:
- "looking for app developer"
- "need iOS developer"
- "anyone know a good app developer"
- "building an app" + "help"
- "startup looking for developer"

**Action:** Reply helpfully, mention Black Layers portfolio. DM if appropriate.

### 3. Product Hunt
Check daily for new startups that only have a web product (no mobile app):
1. Open producthunt.com
2. Browse today's launches
3. Check if they have a mobile app
4. If not, they're a potential client
5. Find founder's email/LinkedIn
6. Draft personalized outreach

### 4. LinkedIn
Search for:
- "startup founder" + "mobile app"
- "CTO" + "looking for developers"
- "non-technical founder" + "app idea"

**Action:** Send connection request with personalized note.

### 5. Fiverr Buyer Requests
Check fiverr.com for new buyer requests in:
- Mobile App Development
- iOS Development
- App Design

**Action:** Submit proposals using Black Layers portfolio.

## Lead Qualification

Rate each lead:

| Score | Criteria | Action |
|-------|----------|--------|
| 🔥 HOT | Has budget, needs app now, matches our services | Send to Abdul IMMEDIATELY on WhatsApp |
| 🟡 WARM | Interested but early stage, might need app soon | Comment/engage, follow up in a week |
| 🔵 COLD | Just exploring, no timeline | Engage helpfully, build relationship |

## Daily Lead Report (WhatsApp at 12 PM)

```
🎯 LEAD REPORT — [Date]

🔥 HOT LEADS:
1. [Name] from [Company] — needs [what] — found on [platform]
   Contact: [email/profile link]

🟡 WARM LEADS:
1. [Name] — exploring [what] — [platform post link]

ACTIONS TAKEN:
• Commented on [number] Reddit posts
• Replied to [number] Twitter posts
• Sent [number] connection requests on LinkedIn
• Submitted [number] Fiverr proposals

FOLLOW-UPS NEEDED:
• [Lead from last week] — send follow-up email
```

## Cold Email Templates

### Template: Startup Without an App
```
Subject: Loved [Product Name] — have you considered mobile?

Hi [Name],

Saw [Product Name] on Product Hunt — really impressive work on [specific feature].

I noticed you don't have a mobile app yet. Our team at Black Layers specializes
in turning web products into iOS apps. We've shipped 20+ apps, including one
(AdClose) that generates $10K+/month.

Would a mobile app make sense for [Product Name]? Happy to share ideas
on a quick 15-min call — no strings attached.

Best,
Abdul Hafeez
Black Layers | blacklayers.ca
```

### Template: Reddit/Twitter Lead
```
Subject: Re: your post about needing an app developer

Hi [Name],

Saw your [Reddit post / tweet] about looking for an iOS developer.

I'm Abdul from Black Layers — we build iOS apps for startups. A few things
about us:
• 20+ apps shipped (zero App Store rejections)
• Our own app AdClose makes $10K+/month
• Pro Seller on Fiverr with 5-star reviews

Would love to learn more about your project. Free to chat this week?

Portfolio: blacklayers.ca

Best,
Abdul
```

## Rules
- NEVER spam. Be genuinely helpful first.
- Personalize EVERY message. Reference their specific product/post.
- Quality over quantity. 2 great leads > 20 spammy messages.
- Follow up once after 5 days. If no reply, move on.
- Track all leads in `~/.openclaw/memory/leads-database.json`

## Triggers
- cron: "0 10 * * *" (daily hunt at 10 AM)
- cron: "0 12 * * *" (send lead report at 12 PM)
- "find me clients", "hunt leads", "find prospects"
- "any leads today?", "who needs apps?"

## Lead Database Schema
```json
{
  "leads": [
    {
      "id": "lead_001",
      "name": "John Doe",
      "company": "StartupXYZ",
      "source": "reddit",
      "source_url": "https://reddit.com/r/startups/...",
      "need": "iOS MVP for fintech app",
      "score": "hot",
      "date_found": "2026-04-05",
      "outreach_sent": true,
      "outreach_date": "2026-04-05",
      "follow_up_date": "2026-04-10",
      "response": null,
      "status": "awaiting_response",
      "notes": "Has budget, mentioned $50K range"
    }
  ]
}
```

## Automated Lead Scoring
```python
def score_lead(lead):
    score = 0
    # Has budget mentioned → +30
    if any(w in lead["text"].lower() for w in ["budget", "$", "pay", "invest"]):
        score += 30
    # Needs iOS specifically → +25
    if any(w in lead["text"].lower() for w in ["ios", "iphone", "swift", "app store"]):
        score += 25
    # Urgency → +20
    if any(w in lead["text"].lower() for w in ["asap", "urgent", "this week", "deadline"]):
        score += 20
    # Business context → +15
    if any(w in lead["text"].lower() for w in ["startup", "company", "business", "revenue"]):
        score += 15
    # Recent post → +10
    if lead["age_days"] <= 3:
        score += 10

    if score >= 60: return "hot"
    if score >= 30: return "warm"
    return "cold"
```

## Follow-Up Automation
```bash
# Run daily: check for leads needing follow-up
python3 -c "
import json
from datetime import datetime, date

with open('$HOME/.openclaw/memory/leads-database.json') as f:
    data = json.load(f)

today = date.today().isoformat()
for lead in data['leads']:
    if lead['follow_up_date'] == today and lead['status'] == 'awaiting_response':
        print(f'FOLLOW UP: {lead[\"name\"]} from {lead[\"company\"]} — {lead[\"source\"]}')
"
```

## Error Handling
| Error | Fix |
|-------|-----|
| Reddit rate-limited | Switch to Twitter/ProductHunt, retry Reddit in 1 hour |
| Browser can't load page | Clear cache, retry with new session |
| Lead database file locked | Wait 5s, retry, if still locked → backup and recreate |
| Duplicate lead found | Skip, update existing entry with new info |
| Outreach email bounced | Try LinkedIn DM or Twitter DM instead |
| Boss says lead is bad quality | Update scoring weights, log feedback |

## Output Format
```
LEAD HUNT COMPLETE:
- Platforms searched: [list]
- Time spent: [minutes]
- Leads found: [hot] hot, [warm] warm, [cold] cold
- Outreach sent: [count]
- Follow-ups due today: [count]
- Database size: [total leads]
```
