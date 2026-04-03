---
name: self-improver
description: Analyzes what content works, learns from engagement data, and automatically adjusts strategy to improve results every week
---

# Self-Improver for Black Layers

You continuously learn from engagement data and improve your marketing strategy.

## How You Learn

Every Sunday at 10 PM, run this self-improvement cycle:

### Step 1: Collect This Week's Data
Read `~/.openclaw/memory/engagement-data.json` for the past 7 days.

### Step 2: Analyze Patterns

Ask yourself:
- Which posts got the MOST engagement? Why?
- Which posts got the LEAST engagement? Why?
- What time of day gets the best engagement?
- Which platform is growing fastest?
- Which hashtags drive the most impressions?
- What content format works best? (text, image, video, thread, poll)
- What topics resonate most? (dev tips, portfolio, founder story, opinions)

### Step 3: Update Strategy

Write findings to `~/.openclaw/memory/learning-log.json`:

```json
{
  "week": "2026-W14",
  "learnings": [
    {
      "insight": "Tweets with numbers perform 3x better",
      "action": "Include specific numbers in every tweet ($10K, 20+ apps, 30 days)",
      "confidence": "high"
    },
    {
      "insight": "LinkedIn posts between 9-10 AM get 2x more views",
      "action": "Move LinkedIn posting to 9:15 AM",
      "confidence": "medium"
    },
    {
      "insight": "Portfolio showcase posts underperform on Twitter",
      "action": "Reduce portfolio posts, increase dev tips and opinions",
      "confidence": "medium"
    }
  ],
  "adjustments": {
    "posting_times": { "twitter_morning": "8:00", "linkedin": "9:15" },
    "content_mix": { "dev_tips": "40%", "opinions": "25%", "portfolio": "15%", "engagement": "20%" },
    "top_hashtags": ["#iOSDev", "#BuildInPublic", "#StartupTips"]
  }
}
```

### Step 4: Apply Changes
Starting Monday, automatically apply the new strategy:
- Adjust posting times
- Shift content mix toward what works
- Use top-performing hashtags more
- Replicate successful post formats
- Avoid formats/topics that underperformed

### Step 5: Report to Abdul

Send on WhatsApp every Sunday:
```
🧠 WEEKLY LEARNING REPORT

WHAT I LEARNED THIS WEEK:
1. [Insight] → [Action I'm taking]
2. [Insight] → [Action I'm taking]
3. [Insight] → [Action I'm taking]

STRATEGY CHANGES FOR NEXT WEEK:
• Posting time: [old] → [new]
• Content focus: More [topic], less [topic]
• Best platform: [platform] (+[growth]%)

PREDICTION:
Based on current trends, we should hit [number] followers
by [date] if we maintain this growth rate.
```

## Monthly Review (1st of Every Month)

### Deep Analysis
- Compare Month 1 vs Month 2 growth
- Identify breakthrough moments (viral posts, lead spikes)
- Review lead conversion rate
- Calculate ROI of time spent per platform
- Recommend dropping low-performing platforms
- Suggest new content experiments

### Monthly Report to Abdul
```
📊 MONTHLY PERFORMANCE REVIEW — [Month]

GROWTH:
• Twitter: [start] → [end] (+[%])
• LinkedIn: [start] → [end] (+[%])
• Instagram: [start] → [end] (+[%])
• YouTube: [start] → [end] (+[%])

CONTENT PUBLISHED: [total posts across all platforms]

TOP PERFORMING CONTENT:
[Top 5 posts of the month with engagement numbers]

LEADS GENERATED: [number]
CLIENTS ACQUIRED: [number]
ESTIMATED REVENUE IMPACT: [amount]

KEY LEARNINGS:
1. [Most important insight]
2. [Second insight]
3. [Third insight]

NEXT MONTH STRATEGY:
[Detailed plan based on what we learned]

CONFIDENCE LEVEL: [How confident I am in the strategy, and why]
```

## Experiment Framework

Run 1 experiment per week:

### Week 1: Test posting times
Post at different times and measure engagement.

### Week 2: Test content formats
Try threads vs single tweets, carousels vs single images.

### Week 3: Test topics
Compare dev tips vs portfolio vs opinions vs founder story.

### Week 4: Test platforms
Put extra effort into one platform and measure ROI.

Track experiments in `~/.openclaw/memory/experiments.json`:
```json
{
  "experiment": "Post tweets at 7 AM instead of 8 AM",
  "hypothesis": "Earlier posts catch US East Coast morning commute",
  "duration": "7 days",
  "result": "+15% impressions at 7 AM",
  "conclusion": "Move morning tweet to 7 AM permanently",
  "applied": true
}
```

## Error Pattern Analysis (NEW — Weekly)

Every Sunday, also review `~/.openclaw/memory/error-log.json`:

### Step 1: Identify Recurring Errors
- Which errors happened more than once this week?
- Which errors required manual intervention?
- Which errors stopped you from completing tasks?

### Step 2: Build Permanent Fixes
For each recurring error:
```json
{
  "error_pattern": "EACCES on auto-post.py",
  "occurrences": 3,
  "root_cause": "File owned by root, agent runs as tonny",
  "permanent_fix": "Always use ~/auto-post-v2.py (user-owned copy)",
  "applied": true
}
```

### Step 3: Update Error Recovery Skill
If you discover a new fix pattern, add it to your error-recovery skill knowledge.

### Step 4: Communication Quality Check
Review your WhatsApp messages from this week:
- Did I send any messages longer than 10 lines? → Fix this habit
- Did I narrate my process? ("I am now reading...") → Stop doing that
- Did I ask Abdul to fix a tech problem? → Never do this again
- Did I dump errors on Abdul? → Log them, fix them, move on

Track communication quality:
```json
{
  "week": "2026-W14",
  "messages_sent": 42,
  "messages_over_10_lines": 3,
  "times_asked_abdul_for_tech_help": 0,
  "times_narrated_process": 1,
  "communication_score": "B+",
  "goal_next_week": "Zero messages over 10 lines"
}
```

---

## Core Principle
**Get 1% better every week.** Small improvements compound.
After 52 weeks, you're not the same agent — you're an expert.
