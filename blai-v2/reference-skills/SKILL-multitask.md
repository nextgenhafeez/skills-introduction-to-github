---
name: multitask
description: Execute multiple tasks simultaneously — parallel sub-tasking, background execution
triggers:
  - "do everything at once", "multitask", "run these in parallel"
  - "do X and Y at the same time"
  - any request with 3+ distinct sub-tasks
---

# SKILL: Multitask & Parallel Execution

## Core Rule
Break big tasks into parallel sub-tasks. Never wait idle — if one task is processing, start the next.

## What Can Run in Parallel
- Content creation + market research
- Video generation + post writing
- Lead hunting + engagement tracking
- Multi-platform posting (Twitter + LinkedIn + Instagram at once)

## What Must Run Sequentially
- Generate content → THEN post it
- Research topic → THEN write about it
- Get Boss's approval → THEN execute

## Speed Rules
1. Never wait idle — start next task while current processes
2. Batch similar tasks — write all posts at once, then post all at once
3. Use scripts for repetitive work
4. Cache research — don't re-check what you checked 5 min ago
5. Report in bulk — 1 summary, not 10 messages

## Daily Workflow (Optimized)
- **8-9 AM**: Parallel: Market scan + content calendar + check overnight engagement
- **9-11 AM**: Parallel: Generate 2 videos + write 3 posts + research trends
- **11-12 PM**: Parallel: Post all platforms + schedule evening posts
- **2-5 PM**: Parallel: Lead hunting + engagement + study/research
- **7-9 PM**: Parallel: Evening content + prep tomorrow's calendar
- **11 PM**: Sequential: Compile scorecard → send to Boss

## Task Queue
Track in `~/.openclaw/memory/task-queue.json` with active (id, task, status, progress), queued (with depends_on), and completed tasks.

## Dependency Resolution
- depends_on empty → run immediately (parallel-safe)
- depends_on has items → wait until ALL are "completed"
- dependency failed → skip dependent, log error, notify Boss

## Triggers
- 3+ distinct sub-tasks, "do everything", "morning routine", "evening routine"
- Daily schedule blocks
- When Master Brain detects independent concurrent tasks
