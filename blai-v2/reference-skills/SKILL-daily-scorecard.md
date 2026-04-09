---
name: daily-scorecard
description: Mandatory nightly accountability report — auto-collects metrics, sends scorecard to Boss at 11 PM
triggers:
  - cron: "0 23 * * *"
  - "send scorecard", "daily report", "how did I do today"
  - "grade yourself", "self assessment"
---

# SKILL: Daily Scorecard

## Purpose
Every night at 11 PM, send Boss a scorecard. No excuses, no fluff — numbers and facts only.

## Scorecard Sections
- **CONTENT**: Posts created/published (which platforms), videos generated/posted
- **LEADS**: Found, outreach sent, responses received
- **ENGAGEMENT**: New followers (all platforms), comments/likes, DMs
- **LEARNING**: What studied today, key insight
- **FAILURES**: What failed, why, fix for tomorrow
- **TOMORROW'S #1 PRIORITY**
- **SELF-GRADE**: ___/10

## Rules
1. Send EVERY night at 11 PM — no exceptions
2. If a number is 0, write 0 — don't hide it
3. Be brutally honest in Failures section
4. 10/10 is almost never real
5. "Rate-limited" is not an excuse — switch to fallback model
6. "Studying" without execution = 0 productivity

## Auto-Collection (10:45 PM)
Gather data from: `~/.openclaw/memory/twitter-analytics.json`, `linkedin-analytics.json`, `leads-database.json`, `engagement-data.json`

## Storage
Save to `~/.openclaw/memory/scorecards/$DATE.json` with all metrics + failures + grade.

## Weekly Aggregation (Sundays)
Calculate weekly averages from scorecards, identify worst area, create fix plan, update self-improver skill, report summary to Boss.

## Boss Uses This For
- Consistent <5/10 → skills need fixing
- Leads always 0 → strategy needs changing
- Content 0 engagement → content strategy needs changing
- Shared with Claude for weekly review

## Remember
Boss needs HONESTY, not perfection. A 3/10 with honest failures beats a fake 8/10.
