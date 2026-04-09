---
name: automation-engine
description: BLAI workflow automation via Make.com (primary) and n8n (backup) for social media, leads, engagement, and scheduling
---

# Automation Engine

## Tools
| Tool | URL | Use For |
|------|-----|---------|
| **Make.com** | eu1.make.com | Social media, integrations (PRIMARY) |
| **n8n** | http://34.132.116.116:5678 | Custom workflows, webhooks (BACKUP) |

Use Make.com first. Only use n8n when Make.com can't handle it.

---

## Workflows

### WF1: Social Media Auto-Poster
- Schedule: 8AM, 2PM, 6PM Morocco time
- Flow: BLAI generates content → Post to Twitter/X + LinkedIn → Log to Google Sheets → WhatsApp confirm to Abdul
- Nodes: Schedule Trigger, HTTP Request (Twitter/LinkedIn API), Google Sheets, WhatsApp
- Twitter API: developer.twitter.com → Create app → API Key/Secret/Access Token → Twitter node "Create Tweet"
- LinkedIn API: linkedin.com/developers → Client ID/Secret → OAuth2 → LinkedIn node "Create Post"

### WF2: Lead Hunter (Automated)
- Schedule: every 4 hours
- Flow: Search Reddit (r/startups, r/entrepreneur, r/forhire, r/smallbusiness) + Twitter/X for keywords ("need an app", "looking for developer", "iOS developer") → Filter duplicates/spam → Score leads 1-10 → Save to Google Sheets → If score >= 7, WhatsApp HOT LEAD alert
- Reddit API: oauth.reddit.com | Twitter Search API
- Scoring: +3 need+app, +3 ios/iphone, +2 budget/pay/hire, +1 startup/business, -5 free/intern

### WF3: Comment & Reply Monitor
- Schedule: every 30 minutes
- Flow: Check Twitter mentions (GET /2/users/:id/mentions) + LinkedIn comments + Instagram comments → Classify (question/compliment/complaint/lead/spam) → Auto-reply if safe, alert Abdul if sensitive → Log to Sheets
- Auto-reply rules: NEVER auto-reply to complaints or unclear context. Keep replies short, friendly, professional. Never pushy. Stay on-platform.

### WF4: Content Calendar
- Weekly trigger: Sunday 8PM
- BLAI generates 7 days content (21 tweets, 7 LinkedIn, 7 Instagram, 3 blog outlines) → Save to Sheets → Abdul approves/edits → Daily trigger reads and posts at scheduled times

### WF5: Analytics Dashboard
- Daily trigger: 7PM Morocco time
- Fetch Twitter/LinkedIn/Instagram/website analytics → Compile daily report → Save to Sheets → WhatsApp summary (followers, impressions, engagement, top/worst performer, tomorrow's focus)

---

## Credentials Needed
| Service | Where |
|---------|-------|
| Twitter/X | developer.twitter.com |
| LinkedIn | linkedin.com/developers |
| Instagram | developers.facebook.com |
| Reddit | reddit.com/prefs/apps |
| Google Sheets/Analytics | console.cloud.google.com |

---

## Platform Strategy

### Twitter/X (@blacklayers) — Goal: 1000 followers/3mo
- 3 tweets/day (8AM/2PM/6PM), reply to 10, like 20, follow 10
- Mix: 40% dev tips, 25% portfolio, 20% news, 15% behind-scenes
- Hashtags: #iOSDeveloper #AppDevelopment #SwiftUI #StartupTech #MobileApp #BlackLayers

### LinkedIn (Abdul Hafeez) — Goal: 500 connections/3mo
- 1 post/day (9AM), comment on 5, send 5 connection requests, reply to all comments
- Mix: 30% case studies, 25% founder journey, 25% insights, 20% testimonials

### Instagram (@blacklayers)
- 1 visual/day, 2-3 Stories, reply to all, engage with 10 accounts
- Mix: 40% app showcases, 25% design tips, 20% motivational, 15% client work

### Reddit — Goal: authority + leads
- Answer 2 questions/day, 1 helpful comment in startup subs. NEVER be promotional.
- Monitor: r/startups, r/entrepreneur, r/smallbusiness, r/iOSProgramming, r/SwiftUI, r/forhire, r/freelance, r/SideProject, r/indiehackers

---

## Customer Communication Rules
- Response time: <1 hour (auto) or <4 hours (manual)
- Tone: friendly, professional, helpful. Never corporate/desperate.
- Do: answer specific questions, show interest, offer tips, share portfolio, ask open-ended questions
- Don't: pitch immediately, copy-paste, ignore negatives, argue, spam links
- Lead flow: helpful reply → provide value/portfolio → offer free consultation → Abdul takes call → convert

## Metrics Targets
| Metric | Month 1 | Month 3 |
|--------|---------|---------|
| Twitter followers | 200 | 1000 |
| LinkedIn connections | 300 | 500 |
| Leads/week | 10 | 25 |
| Hot leads/week | 2 | 5 |
| Client calls/week | 1 | 3 |

**Start with WF1 (Auto-Poster) — foundation for everything else.**
