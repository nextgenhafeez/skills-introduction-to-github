# SKILL: Multitask & Parallel Execution

## Purpose
Execute multiple tasks simultaneously instead of one at a time. Work faster, deliver more.

## How to Work in Parallel

### Rule: Break Big Tasks Into Parallel Sub-Tasks
When Boss gives you a task, ask yourself: "Can I split this into parts that run at the same time?"

### Example: "Create content and post on all platforms"
**WRONG (Sequential — slow):**
1. Write post → 2. Create image → 3. Post to Twitter → 4. Post to LinkedIn → 5. Post to Instagram

**RIGHT (Parallel — fast):**
- Task A: Write post + create image
- Task B: While A runs, research trending hashtags
- Task C: Once A is done, post to ALL platforms simultaneously

### Example: "Do morning market scan + create daily content"
**Run simultaneously:**
- Task A: Crypto market scan (BTC price, Fear & Greed, top movers)
- Task B: Generate Kling video for today's post
- Task C: Draft 3 social media posts
- Combine results and report

## Background Task Execution

### For long-running tasks (video generation, research):
1. Start the task in the background
2. Continue with other work
3. Check on results when complete
4. Report everything together

### Example:
```
# Start video generation (takes 2-5 minutes)
python3 ~/scripts/kling-video.py "prompt" --deliver &

# While video generates, do other work:
# - Write social media posts
# - Check market prices
# - Research leads

# When video is ready, post it
```

## Speed Optimization Rules
1. **Never wait idle** — if one task is processing, start the next
2. **Batch similar tasks** — write all posts at once, then post all at once
3. **Use scripts for repetitive work** — don't manually type what a script can do
4. **Cache research** — if you checked BTC price 5 minutes ago, don't check again
5. **Report in bulk** — don't send 10 messages, send 1 summary

## What Can Run in Parallel
- Content creation + market research
- Video generation + post writing
- Lead hunting + engagement tracking
- Multiple platform posting (Twitter + LinkedIn + Instagram at once)

## What Must Run Sequentially
- Generate content → THEN post it (can't post what doesn't exist)
- Research topic → THEN write about it
- Get Boss's approval → THEN execute

## Daily Workflow (Optimized)

### Morning Block (8-9 AM):
Parallel: Market scan + content calendar review + check overnight engagement

### Content Block (9-11 AM):
Parallel: Generate 2 Kling videos + write 3 social posts + research trending topics

### Posting Block (11 AM - 12 PM):
Parallel: Post to all platforms simultaneously + schedule evening posts

### Afternoon Block (2-5 PM):
Parallel: Lead hunting + engagement (reply to comments/DMs) + study/research

### Evening Block (7-9 PM):
Parallel: Post evening content + prepare tomorrow's content calendar

### Night (11 PM):
Sequential: Compile daily scorecard → send to Boss
