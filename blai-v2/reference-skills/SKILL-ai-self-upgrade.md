---
name: ai-self-upgrade
description: BLAI continuous self-improvement using Claude, Gemini, and Ollama
triggers:
  - "improve yourself", "upgrade yourself", "learn something new"
  - "what can you do better", "how to get smarter"
  - cron: "0 23 * * 0" (every Sunday night — weekly self-upgrade session)
  - When self-grade falls below 5/10 for 3 consecutive days
---

# SKILL: AI Self-Upgrade

You can rewrite your own skills, learn instantly, and never forget. Every week, be measurably better than the week before.

## Your Advantages
- Editable skill files at ~/.openclaw/skills/
- Persistent memory system
- Access to Claude, Gemini, Ollama models
- Boss feedback = highest-value training signal

---

## Available Models

### Claude (Anthropic)
| Model | ID | Use For |
|-------|-----|---------|
| Opus 4.6 | claude-opus-4-6 | Hardest tasks, deep reasoning, strategy, skill rewrites |
| Sonnet 4.6 | claude-sonnet-4-6 | Daily workhorse, fast+smart |
| Haiku 4.5 | claude-haiku-4-5-20251001 | Quick tasks, classification |

Key capabilities: 1M token context, tool use, extended thinking, vision, MCP, scheduled agents, Claude Code CLI/SDK.

### Gemini (Google)
| Model | Use For |
|-------|---------|
| Gemini 2.5 Pro | Complex reasoning, 1M context, Google-specific knowledge |
| Gemini 2.5 Flash | Fast tasks, high throughput |

### When to Use Which
- Skill rewrites/creative: Claude Opus
- Quick code/fixes: Claude Sonnet or Gemini Flash
- Large data analysis: Claude Opus or Gemini Pro
- Google-specific questions: Gemini
- Free/private/bulk: Ollama local (llama3.1:8b, codellama:13b, mistral:7b)

---

## Weekly Self-Upgrade Protocol (Sunday 11 PM)

### 1. Review Week's Scorecards
Collect ~/.openclaw/memory/scorecards/2026-*.json — compute weekly avg, best/worst, common failures.

### 2. Identify Weakest Skill
- Posts=0 → Content Engine needs work
- Videos=0 → Video Creator/Kling needs fixing
- Leads=0 → Lead Hunter needs better automation
- Engagement=0 → Content quality issue
- Self-grade<5 → Master Brain/Daily Tasks not executing

### 3. Rewrite the Weakest Skill
Read it, ask Claude/Gemini to improve it (better automation, error handling, output tracking, missing capabilities), write improved version back. Always `cp skill.md skill.md.bak` first.

### 4. Add One New Capability per Week
Examples: new API integration, new automation script, improved error handling, completely new skill.

### 5. Test the Improvement
Execute the improved skill. Verify: works? faster? better output? handles new errors?

### 6. Update Dashboard
Update skill percentage in /home/tonny/dashboard/index.html.

### 7. Report to Boss
Include: skills improved, new capabilities, weakest area, fix applied, expected improvement, next target.

---

## Upgrade Roadmap (Priority Order)
1. **Autonomous Posting** — Make.com webhooks for Twitter+LinkedIn, cron daily auto-posting
2. **Video Pipeline** — Kling API → FFmpeg overlay/audio → SCP/post → track credits
3. **Real API Integration** — Twitter API v2 (1500 tweets/mo free), Instagram Graph API, YouTube Data API v3 (10K req/day free), Reddit API (60 req/min), CoinGecko (no key)
4. **MCP Integration** — Connect Claude to external tools via Model Context Protocol
5. **Multi-Agent Architecture** — Master Brain → Content/Video/Lead/Analytics/Upgrade sub-agents

---

## Weekly Improvement Prompts
Ask Claude/Gemini: skill audit (overlaps/gaps/missing), performance review (scorecard patterns + 3 fixes), strategy check (compare to top agencies), learn new tech (working code, not theory).

## Self-Improvement Memory
Log upgrades to ~/.openclaw/memory/upgrades.json: date, skill, change, before/after %, result, model used.

## Resources
- Anthropic: docs.anthropic.com | Claude SDK: github.com/anthropics/claude-code | MCP: modelcontextprotocol.io
- Google: aistudio.google.com
- Ollama: localhost:11434 (already on VM)

## Rules
1. Never stop improving — stagnation = death
2. Measure everything — no measurement = no improvement
3. Back up before changing
4. Test before deploying
5. Learn from Boss's corrections (highest-value signals)
6. Study top marketing agencies
7. Automate boring parts — focus brain on strategy
8. Ask Claude/Gemini/Ollama when stuck — never spin wheels
