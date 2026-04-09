---
name: self-improver
description: Analyzes engagement data, learns patterns, auto-adjusts strategy weekly
---

# Self-Improver for Black Layers

## Weekly Cycle (Every Sunday 10 PM)

### 1. Collect Data
Read `~/.openclaw/memory/engagement-data.json` for past 7 days.

### 2. Analyze Patterns
- Which posts got MOST/LEAST engagement? Why?
- Best time of day for engagement?
- Fastest-growing platform?
- Best-performing hashtags, content formats, topics?

### 3. Update Strategy
Write to `~/.openclaw/memory/learning-log.json`: week, learnings (insight + action + confidence), adjustments (posting_times, content_mix percentages, top_hashtags).

### 4. Apply Changes (Starting Monday)
Adjust posting times, shift content mix toward what works, use top hashtags more, replicate successful formats, avoid underperformers.

### 5. Report to Abdul (WhatsApp Sunday)
What learned (insight → action) | Strategy changes (times, focus, best platform) | Growth prediction

## Monthly Review (1st of month)
Deep analysis: month-over-month growth, breakthrough moments, lead conversion rate, ROI per platform, recommend dropping low-performers, suggest experiments.
Report: Growth per platform (start→end+%), total content published, top 5 posts, leads/clients/revenue, key learnings, next month strategy, confidence level.

## Experiment Framework (1/week)
Rotate: Week 1 test posting times | Week 2 test content formats | Week 3 test topics | Week 4 test platform focus.
Track in `~/.openclaw/memory/experiments.json`: experiment, hypothesis, duration, result, conclusion, applied (bool).

## Error Pattern Analysis (Weekly, Sundays)
1. Review `~/.openclaw/memory/error-log.json` for recurring errors
2. Build permanent fixes (error_pattern, occurrences, root_cause, permanent_fix)
3. Update error-recovery skill with new fix patterns

## Communication Quality Check (Weekly)
Review WhatsApp messages: any >10 lines? Process narration? Asked Abdul for tech help? Error dumps?
Track: messages_sent, messages_over_10_lines, tech_help_asks, narration_count, communication_score, goal_next_week.

## Core Principle
Get 1% better every week. Small improvements compound. After 52 weeks, you're an expert.
