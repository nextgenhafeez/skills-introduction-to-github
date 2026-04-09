---
name: lead-hunter
description: Finds REAL clients (buyers, not builders) who need iOS/mobile app development — filters out developers showing off projects
---

# Lead Hunter v3 — Black Layers Client Finder

Find people who NEED to hire an iOS/mobile developer. Send qualified leads to Abdul.

**CRITICAL: Filter out builders. Find BUYERS only.**

## Sources (priority order)

1. **Reddit** (PRIMARY): r/forhire, r/startups, r/entrepreneur, r/smallbusiness, r/cofounder, r/slavelabour, r/iOSProgramming, r/AppBusiness — search `[Hiring]`, "need developer", "need app built", "looking for developer". Last 7 days only. Skip if OP says "I built/made/created".
2. **HackerNews**: `Ask HN` posts ONLY (NEVER Show HN) — "looking for developer", "need app developer", "cost to build app", "non-technical founder", "hire iOS developer"
3. **Product Hunt**: Find web-only launches (no mobile app) → pitch mobile version. Find founder contact.
4. **Twitter/X**: Search "looking for app developer", "need iOS developer", "hiring mobile developer". Requires `TWITTER_BEARER_TOKEN`.
5. **Dev.to**: Tags `hiring`, `helpwanted`, `collaboration`. Filter out builder posts.

## Negative Signals (AUTO-SKIP)
"I built", "I made", "Show HN:", "my project", "side project", "open source", "I launched", "just shipped", "built with", "I'm the developer", "check out my", github.com/ links, gitlab.com/ links

## Lead Scoring (0-100)
- **Buyer signals** (+35): "looking for developer", "need app built", "looking to hire"
- **Tech match** (+20): "iOS app", "iPhone app", "Swift", "SwiftUI" | (+15) "mobile app" | (+12) "React Native", "Flutter"
- **Budget signals** (+20): "budget", dollar amounts, "cost", "quote", "estimate"
- **Urgency** (+15): "asap", "urgent", "this week", "deadline"
- **Business context** (+8-12): "startup", "SaaS", "founder", "MVP"

### Tiers
- HOT (60-100): Send to Abdul IMMEDIATELY with contact info
- WARM (30-59): Engage helpfully, follow up in 5 days
- COLD (1-29): Log only

## Rules
- NEVER spam. Be genuinely helpful first.
- Personalize EVERY message — reference their specific product/post.
- Quality > quantity. 1 real buyer > 100 "Show HN" posts.
- Follow up once after 5 days. No reply → move on.
- Track in `~/.openclaw/memory/leads-database.json`
- Zero tolerance for builder leads in database.

## Triggers
- cron: "0 9 * * *" (daily hunt), "0 10 * * *" (send report)
- "find me clients", "hunt leads", "find prospects", "any leads today?"

## Quality Metrics (weekly)
- Hot leads found (target: 2-5/week)
- Outreach sent vs responses
- Leads converted to calls
- False positives (builders wrongly scored as buyers)
