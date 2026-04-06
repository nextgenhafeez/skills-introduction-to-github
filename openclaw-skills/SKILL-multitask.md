---
name: multitask
description: Execute multiple tasks simultaneously — parallel sub-tasking, background execution, speed optimization
triggers:
  - "do everything at once"
  - "multitask"
  - "run these in parallel"
  - "do X and Y at the same time"
  - any request with 3+ distinct sub-tasks
---

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

---

## Triggers
- Any request containing 3+ distinct sub-tasks
- "do everything", "handle all of this", "morning routine", "evening routine"
- Daily schedule blocks (morning/content/posting/afternoon/evening)
- When Master Brain detects independent tasks that can run concurrently

## Task Queue Management

### How to Track Parallel Tasks
Maintain a live task queue in `~/.openclaw/memory/task-queue.json`:
```json
{
  "active": [
    {"id": "t1", "task": "Generate Kling video", "status": "running", "started": "09:01", "progress": 60},
    {"id": "t2", "task": "Write 3 social posts", "status": "running", "started": "09:01", "progress": 80}
  ],
  "queued": [
    {"id": "t3", "task": "Post to all platforms", "depends_on": ["t1", "t2"]}
  ],
  "completed": [
    {"id": "t0", "task": "Morning market scan", "completed": "08:45", "result": "success"}
  ]
}
```

### Dependency Resolution
Before starting a task, check if it depends on another:
```
IF task.depends_on is empty → run immediately (parallel-safe)
IF task.depends_on has items → wait until ALL dependencies are "completed"
IF dependency failed → skip dependent task, log error, notify Boss
```

## Error Handling
| Error | Fix |
|-------|-----|
| Background task hangs (>10 min) | Kill process, log timeout, move to next task |
| Parallel tasks conflict (same file) | Queue the conflicting task, run sequentially |
| Memory/CPU overload | Reduce parallel tasks to 2, increase timeouts |
| Task fails mid-batch | Log failure, continue other tasks, retry failed one at end |
| Boss sends urgent request mid-batch | Pause lowest-priority task, handle urgent request first |

## Output Format
After completing a multitask batch:
```
MULTITASK BATCH COMPLETE:
- Total tasks: [count]
- Parallel groups: [count]
- Completed: [count] ([time elapsed])
- Failed: [count] (reasons: ...)
- Results: [summary of each task outcome]
- Time saved vs sequential: ~[estimate]
```
