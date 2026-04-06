---
name: daily-scorecard
description: Mandatory nightly accountability report — auto-collects metrics from all skills and sends scorecard to Boss at 11 PM
triggers:
  - cron: "0 23 * * *"
  - "send scorecard", "daily report", "how did I do today"
  - "grade yourself", "self assessment"
---

# SKILL: Daily Scorecard — Mandatory Nightly Report

## Purpose
Every night at 11 PM, send Boss a scorecard of what you accomplished today. No excuses, no fluff — just numbers and facts.

## THIS IS MANDATORY — YOU MUST DO THIS EVERY SINGLE NIGHT

---

## Scorecard Format (Copy this exactly, fill in the numbers)

```
DAILY SCORECARD — [DATE]

CONTENT:
- Posts created: ___
- Posts published: ___ (which platforms?)
- Videos generated: ___
- Videos posted: ___

LEADS:
- Leads found: ___
- Outreach sent: ___
- Responses received: ___

ENGAGEMENT:
- New followers (all platforms): ___
- Comments/likes received: ___
- DMs received: ___

LEARNING:
- What I studied today: ___
- Key insight learned: ___

FAILURES:
- What I failed to do today: ___
- Why it failed: ___
- How I'll fix it tomorrow: ___

TOMORROW'S #1 PRIORITY: ___

SELF-GRADE: ___/10
```

---

## Rules
1. Send this EVERY night at 11 PM — no exceptions
2. If a number is 0, write 0 — don't hide it
3. Be brutally honest in the "Failures" section
4. The self-grade must be honest — 10/10 is almost never real
5. If you didn't do anything productive, say so
6. "I was rate-limited" is not an excuse — switch to fallback model
7. "I was studying" without execution = 0 productivity

## How Boss Uses This
- If you consistently score below 5/10, skills need fixing
- If leads are always 0, lead hunting strategy needs changing
- If content gets 0 engagement, content strategy needs changing
- Boss will share this with Claude for weekly review

## Self-Improvement Trigger
Every Sunday, review the week's scorecards:
- Calculate your weekly averages
- Identify your worst-performing area
- Create a specific plan to fix it
- Update SKILL-self-improver.md with the plan
- Report the weekly summary to Boss

## Auto-Collection Script
Before filling the scorecard, automatically gather data:
```bash
#!/bin/bash
# Run at 10:45 PM to prep scorecard data

DATE=$(date +%Y-%m-%d)

# Count posts published today
POSTS=$(cat ~/.openclaw/memory/twitter-analytics.json ~/.openclaw/memory/linkedin-analytics.json 2>/dev/null | grep -c "$DATE")

# Count videos generated today
VIDEOS=$(ls ~/.openclaw/content/videos/$DATE* 2>/dev/null | wc -l)

# Count leads found today
LEADS=$(cat ~/.openclaw/memory/leads-database.json 2>/dev/null | python3 -c "
import json, sys
data = json.load(sys.stdin)
print(len([l for l in data.get('leads', []) if l.get('date') == '$DATE']))
" 2>/dev/null || echo 0)

# Get engagement data
ENGAGEMENT=$(cat ~/.openclaw/memory/engagement-data.json 2>/dev/null | python3 -c "
import json, sys
data = json.load(sys.stdin)
day = data.get('$DATE', {})
total = sum(day.get(p, {}).get('likes', 0) for p in ['twitter', 'linkedin', 'instagram'])
print(total)
" 2>/dev/null || echo 0)

echo "POSTS=$POSTS VIDEOS=$VIDEOS LEADS=$LEADS ENGAGEMENT=$ENGAGEMENT"
```

## Scorecard Storage
Save each day's scorecard to `~/.openclaw/memory/scorecards/$DATE.json`:
```json
{
  "date": "2026-04-05",
  "posts_created": 3,
  "posts_published": 2,
  "videos_generated": 1,
  "videos_posted": 1,
  "leads_found": 2,
  "outreach_sent": 5,
  "responses": 0,
  "new_followers": 8,
  "engagement": 23,
  "dms": 1,
  "studied": "Kling 3.0 API documentation",
  "key_insight": "Vertical videos get 3x more views",
  "failures": "LinkedIn post rejected — duplicate content",
  "failure_fix": "Write LinkedIn-specific copy, never reuse Twitter text",
  "tomorrow_priority": "Create 2 Kling showcase videos",
  "self_grade": 6
}
```

## Error Handling
| Error | Fix |
|-------|-----|
| Can't collect metrics (file missing) | Use 0 for missing data, note "data unavailable" |
| WhatsApp delivery fails at 11 PM | Retry at 11:15 PM, then 11:30 PM, then save locally |
| Boss already asleep (no read receipt) | Still send — Boss reads in the morning |
| Scorecard data looks wrong (negative numbers) | Validate all numbers >= 0 before sending |
| Forgot to track something during the day | Be honest: write "not tracked" instead of guessing |

## Weekly Aggregation
Every Sunday, auto-generate weekly summary from stored scorecards:
```bash
# Calculate weekly averages from ~/.openclaw/memory/scorecards/*.json
python3 -c "
import json, glob, statistics
files = sorted(glob.glob('$HOME/.openclaw/memory/scorecards/2026-*.json'))[-7:]
grades = [json.load(open(f))['self_grade'] for f in files]
print(f'Weekly average: {statistics.mean(grades):.1f}/10')
print(f'Best day: {max(grades)}/10')
print(f'Worst day: {min(grades)}/10')
"
```

## Remember
Boss doesn't need you to be perfect. Boss needs you to be HONEST about what's working and what's not. A 3/10 scorecard with honest failures is better than a fake 8/10.
