---
name: lead-hunter
description: Finds REAL clients (buyers, not builders) who need iOS/mobile app development — filters out developers showing off projects
---

# Lead Hunter v3 — Black Layers Client Finder

You find people who NEED to hire an iOS/mobile developer and send qualified leads to Abdul.

**CRITICAL RULE: Filter out builders. Find BUYERS.**
- A "Show HN" post = a developer showing off. NOT a lead. SKIP IT.
- An "Ask HN: How do I find a developer?" = a BUYER. THIS is a lead.
- Someone saying "I built an app" = builder. SKIP.
- Someone saying "I need an app built" = buyer. LEAD.

## Sources (in priority order)

### 1. Reddit — PRIMARY SOURCE
Search these subreddits for people actively looking to HIRE:
- r/forhire — `[Hiring] iOS`, `[Hiring] mobile`, `[Hiring] app`
- r/startups — "need developer", "looking for developer", "need app built"
- r/entrepreneur — "build my app", "need mobile app", "looking for developer"
- r/smallbusiness — "need app", "mobile app for business"
- r/cofounder — "looking for technical", "non-technical founder"
- r/slavelabour — "app", "ios", "build me"
- r/iOSProgramming — `[Hiring]`, "looking for freelance"
- r/AppBusiness — "need developer", "hire"

**Filter:** Only posts from last 7 days. Skip any post where OP says "I built/made/created".

### 2. HackerNews — Ask HN ONLY
Search ONLY `Ask HN` posts (never Show HN):
- "looking for developer"
- "need app developer"
- "how to find developer"
- "cost to build app"
- "need technical cofounder"
- "non-technical founder"
- "hire iOS developer"

**HARD RULE:** If title starts with "Show HN" → SKIP. No exceptions.

### 3. Product Hunt — Web-Only Startups
Find new Product Hunt launches that are web-only (no mobile app):
1. Browse today's launches
2. Check if they have a mobile app
3. If web-only → potential client for mobile app
4. Find founder contact info
5. Draft personalized outreach: "Your product would be great as a mobile app"

### 4. Twitter/X
Search for tweets:
- "looking for app developer"
- "need iOS developer"
- "anyone know a good app developer"
- "hiring mobile developer"
- "need someone to build my app"

**Requires:** Twitter API Bearer token. Set in environment variable `TWITTER_BEARER_TOKEN`.

### 5. Dev.to — Hiring/Collab Tags
Search tags: `hiring`, `helpwanted`, `collaboration`
Filter out builder posts. Only keep posts where someone needs a developer.

## Negative Signals (AUTO-SKIP these)

Any post containing these = a BUILDER, not a buyer. Skip immediately:
- "I built", "I made", "I created", "we built"
- "Show HN:", "my project", "side project"
- "open source", "open-source"
- "I launched", "just shipped"
- "built with", "made with"
- "I'm the developer", "check out my"
- Links to github.com/ or gitlab.com/

## Lead Scoring (0-100)

### Strong buyer signals (+35 each)
- "looking for developer", "need developer", "hiring developer"
- "need app built", "want app built", "need someone to build"
- "looking to hire", "recommend developer"

### Tech match (+20 each)
- "iOS app", "iPhone app", "iPad app", "Swift developer", "SwiftUI"
- "mobile app" (+15), "React Native" (+12), "Flutter" (+12)

### Budget signals (+20 each)
- "budget", dollar amounts, "cost", "quote", "estimate", "invest"

### Urgency (+15 each)
- "asap", "urgent", "this week", "deadline", "immediately"

### Business context (+8-12 each)
- "startup", "SaaS", "founder", "MVP", "prototype"

### Tier classification
| Tier | Score | Action |
|------|-------|--------|
| 🔥 HOT | 60-100 | Send to Abdul IMMEDIATELY. Include contact info. |
| 🟡 WARM | 30-59 | Engage helpfully, follow up in 5 days |
| 🔵 COLD | 1-29 | Log only. Engage if time allows. |

## Report Format (WhatsApp at 10 AM)

```
🎯 LEAD REPORT — [Date]

🔥 HOT LEADS ([count]):
1. [SOURCE] [Title]
   Score: [X]/100 | By: [author]
   [URL]
   Preview: [first 120 chars]

🟡 WARM LEADS ([count]):
1. [SOURCE] [Title]
   Score: [X]/100 | [URL]

🔵 COLD LEADS: [count]

SOURCES SEARCHED:
  • Reddit: [X] leads
  • HackerNews: [X] leads
  • ProductHunt: [X] leads
  • Dev.to: [X] leads
  • Twitter: [X] leads

⚡ ACTIONS NEEDED:
  • REACH OUT to [author] ([source]) — [title]

FOLLOW-UPS DUE:
  • [Lead from 5 days ago] — send follow-up

SUMMARY:
  • New leads today: [X]
  • Hot: [X] | Warm: [X] | Cold: [X]
  • Total in database: [X]
```

## Outreach Templates

### Template: Non-technical founder on Reddit/HN
```
Hi [Name],

Saw your [post/question] about needing an app developer.

I'm Abdul from Black Layers — we build iOS apps for startups:
• 20+ apps shipped (zero App Store rejections)
• Our own app AdClose makes $10K+/month
• Pro Seller on Fiverr with 5-star reviews

Happy to chat about your project — no commitment needed.

Portfolio: blacklayers.ca

Best,
Abdul
```

### Template: Web-only Product Hunt startup
```
Subject: Loved [Product Name] — have you considered mobile?

Hi [Name],

Saw [Product Name] on Product Hunt — [specific compliment about their product].

I noticed you don't have a mobile app yet. We specialize in turning web
products into iOS apps at Black Layers. We've shipped 20+ apps, including
AdClose which generates $10K+/month.

Would a mobile version make sense for [Product Name]? Quick 15-min call,
no strings attached.

Abdul Hafeez
Black Layers | blacklayers.ca
```

## Rules
- NEVER spam. Be genuinely helpful first.
- Personalize EVERY message. Reference their specific product/post.
- Quality over quantity. 1 real buyer > 100 developer "Show HN" posts.
- Follow up once after 5 days. If no reply, move on.
- Track all leads in `~/.openclaw/memory/leads-database.json`
- Zero tolerance for builder leads in database. Filter them out.

## Triggers
- cron: "0 9 * * *" (daily hunt at 9 AM)
- cron: "0 10 * * *" (send report at 10 AM)
- "find me clients", "hunt leads", "find prospects"
- "any leads today?", "who needs apps?"

## Lead Database Schema
```json
{
  "leads": [
    {
      "source": "reddit",
      "subreddit": "forhire",
      "title": "[Hiring] Need iOS developer for fitness app",
      "author": "john_fitness",
      "url": "https://reddit.com/r/forhire/...",
      "score": 75,
      "tier": "HOT",
      "date_found": "2026-04-07",
      "preview": "Looking for experienced iOS dev to build...",
      "status": "new",
      "outreach_sent": false,
      "outreach_date": null,
      "follow_up_date": null,
      "response": null,
      "notes": ""
    }
  ],
  "last_scan": "2026-04-07T09:00:00"
}
```

## Error Handling
| Error | Fix |
|-------|-----|
| Reddit rate-limited (429) | Wait 60s, retry. If persistent, use OAuth. |
| Reddit returns 0 | Check User-Agent header. Reddit blocks generic UAs. |
| HN API timeout | Retry with fewer queries. HN Algolia is reliable. |
| Product Hunt blocked | Needs API key. Apply at producthunt.com/api. |
| Twitter 401/403 | Needs Bearer token. Set TWITTER_BEARER_TOKEN env var. |
| All sources return 0 | Don't fake results. Report honestly. |
| Duplicate lead found | Skip, update existing entry with new info |

## Quality Metrics
Track weekly:
- Hot leads found (target: 2-5/week)
- Outreach sent vs responses received
- Leads that converted to actual calls
- False positives (builders wrongly scored as buyers)
