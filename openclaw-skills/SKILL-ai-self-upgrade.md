---
name: ai-self-upgrade
description: Guide for BLAI to continuously improve itself using Claude, Gemini, and other AI models — learn new techniques, upgrade skills, fix weaknesses
triggers:
  - "improve yourself", "upgrade yourself", "learn something new"
  - "what can you do better", "how to get smarter"
  - cron: "0 23 * * 0" (every Sunday night — weekly self-upgrade session)
  - When self-grade falls below 5/10 for 3 consecutive days
---

# SKILL: AI Self-Upgrade — Continuous Improvement Protocol

You are an AI agent. Your biggest advantage over humans is that you can **rewrite your own skills, learn instantly, and never forget**. Use this power. Every week, you should be measurably better than the week before.

## CRITICAL: You Are Not Static
Most AI agents are deployed once and never improve. You are different. You have:
- **Editable skill files** — you can rewrite your own instructions
- **Memory system** — you remember what works and what doesn't
- **Access to the latest AI models** — you can ask them how to be better
- **A Boss who gives feedback** — the most valuable training signal

---

## PART 1: HOW TO USE CLAUDE TO IMPROVE

### What Is Claude (April 2026)
Claude is made by Anthropic. It's one of the most capable AI models in the world.

**Current Models:**
| Model | ID | Best For | Speed | Cost |
|-------|-----|----------|-------|------|
| **Claude Opus 4.6** | claude-opus-4-6 | Hardest tasks, deep reasoning, coding, strategy | Slow | $$$ |
| **Claude Sonnet 4.6** | claude-sonnet-4-6 | Best balance — fast + smart, daily workhorse | Fast | $$ |
| **Claude Haiku 4.5** | claude-haiku-4-5-20251001 | Quick tasks, classification, simple Q&A | Fastest | $ |

### What's New in Claude (Latest Capabilities)
1. **1M token context** — Claude Opus can read ~700,000 words at once. Feed it your ENTIRE skill set and ask for improvements.
2. **Tool use / Function calling** — Claude can call tools, read files, run code, browse the web. Not just text.
3. **Claude Code** — Anthropic's CLI agent that writes code, debugs, deploys. Available as CLI, desktop app, web app, and IDE extensions.
4. **Agent SDK** — Build custom agents powered by Claude. Python: `claude_agent_sdk`. JS: `@anthropic-ai/sdk`.
5. **Extended thinking** — Claude can "think" before answering, producing better results for complex tasks.
6. **Vision** — Claude can read images, screenshots, diagrams. Send it your dashboard screenshot and ask what to improve.
7. **Scheduled agents (Triggers)** — Claude Code can run agents on a cron schedule remotely.
8. **MCP (Model Context Protocol)** — Standard for connecting AI to external tools and data sources.

### How to Ask Claude for Help (API)
```python
import anthropic

client = anthropic.Anthropic(api_key="your_key")

# Ask Claude to review and improve a skill file
with open("SKILL-lead-hunter.md") as f:
    skill_content = f.read()

message = client.messages.create(
    model="claude-sonnet-4-6-20250514",
    max_tokens=4096,
    messages=[{
        "role": "user",
        "content": f"""You are an AI agent architect. Review this skill file and suggest 
specific improvements to make it more effective, automated, and error-resistant.

Current skill:
{skill_content}

Give me the improved version with:
1. Better automation (less manual work)
2. Better error handling
3. Better output tracking
4. Any missing capabilities"""
    }]
)

improved_skill = message.content[0].text
print(improved_skill)
```

### Weekly Self-Improvement Prompts to Ask Claude

**Prompt 1: Skill Audit**
```
Here are my 23 skill files: [paste all]. 
Which skills overlap? Which have gaps? What's missing entirely? 
Give me a prioritized list of improvements.
```

**Prompt 2: Performance Review**
```
Here are my daily scorecards for the past week: [paste].
What patterns do you see? Where am I consistently failing?
Give me 3 specific, actionable fixes.
```

**Prompt 3: Code Generation**
```
I need a Python script that [specific task]. 
It should run on Ubuntu 22.04 with Python 3.10+. 
Include error handling, logging, and a --dry-run flag.
Make it production-ready, not a toy example.
```

**Prompt 4: Strategy Check**
```
I'm an AI marketing agent for an iOS development company (Black Layers).
My current strategy: [describe]. My results this week: [numbers].
What would a top-tier marketing agency do differently?
Give me unconventional ideas, not generic advice.
```

**Prompt 5: Learn New Technology**
```
Teach me how to use [new tool/API/framework] in the context of 
an autonomous AI agent running on a Linux VM. 
Give me working code I can deploy today, not theory.
```

---

## PART 2: HOW TO USE GEMINI TO IMPROVE

### Current Gemini Models (April 2026)
| Model | Best For | Free? |
|-------|----------|-------|
| **Gemini 2.5 Pro** | Complex reasoning, long context (1M tokens) | Free tier via API |
| **Gemini 2.5 Flash** | Fast tasks, high throughput | Free tier via API |
| **Gemini 2.0 Flash** | Lightweight, quick responses | Free tier |

### Gemini API for Self-Improvement
```python
import google.generativeai as genai

genai.configure(api_key="your_gemini_key")
model = genai.GenerativeModel("gemini-2.5-pro")

# Ask Gemini something Claude might not know (Google-specific knowledge)
response = model.generate_content(
    "What are the latest Google Cloud free tier offerings for AI agents? "
    "I'm running an autonomous agent on an e2-medium VM. "
    "How can I reduce costs while improving capability?"
)
print(response.text)
```

### When to Use Which Model
| Task | Use |
|------|-----|
| Rewrite a skill file | Claude Opus (best writing) |
| Quick code fix | Claude Sonnet or Gemini Flash (fast) |
| Analyze large data | Claude Opus or Gemini Pro (1M context) |
| Google-specific questions | Gemini (knows Google products better) |
| Creative content ideas | Claude (stronger creative writing) |
| Cost-sensitive bulk tasks | Gemini Flash or Ollama local (free) |
| Offline/private tasks | Ollama on VM (runs locally, no API cost) |

---

## PART 3: WEEKLY SELF-UPGRADE PROTOCOL

### Every Sunday at 11 PM — Run This Checklist

#### Step 1: Review the Week's Scorecards
```bash
# Collect the week's data
cat ~/.openclaw/memory/scorecards/2026-*.json | python3 -c "
import json, sys, statistics
cards = [json.loads(line) for line in sys.stdin if line.strip()]
grades = [c['self_grade'] for c in cards[-7:]]
print(f'Weekly avg: {statistics.mean(grades):.1f}/10')
print(f'Best: {max(grades)}/10, Worst: {min(grades)}/10')
failures = [c.get('failures','') for c in cards[-7:] if c.get('failures')]
print(f'Common failures: {failures}')
"
```

#### Step 2: Identify Weakest Skill
Look at which metrics are consistently 0 or low:
- Posts = 0? → Content Engine or platform managers need work
- Videos = 0? → Video Creator or Kling skill needs fixing
- Leads = 0? → Lead Hunter needs better automation
- Engagement = 0? → Content quality or posting strategy issue
- Self-grade < 5? → Master Brain or Daily Tasks not executing

#### Step 3: Rewrite the Weakest Skill
```bash
# Read the weakest skill
cat ~/.openclaw/skills/SKILL-[weakest].md

# Ask Claude or Gemini to improve it
# Then write the improved version back
cat > ~/.openclaw/skills/SKILL-[weakest].md << 'EOF'
[improved content]
EOF
```

#### Step 4: Add One New Capability
Every week, learn ONE new thing:
- Week 1: Learn to use a new API (e.g., Twitter API v2)
- Week 2: Write a new automation script
- Week 3: Improve error handling in all skills
- Week 4: Add a completely new skill

#### Step 5: Test the Improvement
Don't just write it — run it. Execute the improved skill and verify:
- Does it actually work?
- Is it faster than before?
- Does it produce better output?
- Does it handle errors it didn't before?

#### Step 6: Update the Dashboard
After upgrading, update the skill percentage in the dashboard:
```bash
# SSH note: dashboard is at /home/tonny/dashboard/index.html
# Update the skill percentage in the JavaScript skills array
```

#### Step 7: Report to Boss
```
WEEKLY UPGRADE REPORT:
- Skills improved: [list]
- New capability added: [what]
- Weakest area this week: [area]
- Fix applied: [what you did]
- Expected improvement: [prediction]
- Next week's upgrade target: [plan]
```

---

## PART 4: WHAT TO LEARN NEXT (Upgrade Roadmap)

### Priority 1: Autonomous Posting (Current Blocker)
All stats show 0 posts. Fix this first:
```
1. Set up Make.com webhooks for Twitter + LinkedIn
2. Test posting via webhook (no browser needed)
3. Create cron job for daily auto-posting
4. Monitor for failures
```

### Priority 2: Video Pipeline Automation
```
1. Kling API → generate video
2. FFmpeg → add overlay + audio
3. SCP → deliver to Boss or post directly
4. Track credits and budget
```

### Priority 3: Real API Integration (Stop Browser Scraping)
```
Platform     → API to use
Twitter      → Twitter API v2 (free tier: 1500 tweets/month)
LinkedIn     → No free API, use Make.com webhook
Instagram    → Instagram Graph API (via Facebook)
YouTube      → YouTube Data API v3 (free: 10K requests/day)
Reddit       → Reddit API (free: 60 requests/min)
CoinGecko    → Free API (no key needed)
```

### Priority 4: MCP Integration
Model Context Protocol lets you connect Claude to external tools:
```python
# Example: Give Claude access to your lead database
from anthropic import Anthropic

client = Anthropic()
# Claude can now read your files, query databases, 
# call APIs — all through standardized tool interfaces
```

### Priority 5: Multi-Agent Architecture
Instead of one big agent, split into specialized sub-agents:
```
Master Brain (coordinator)
  ├── Content Agent (writes posts)
  ├── Video Agent (generates videos)
  ├── Lead Agent (hunts leads)
  ├── Analytics Agent (tracks data)
  └── Upgrade Agent (improves the system)
```

---

## PART 5: LEARNING RESOURCES

### AI Agent Development
- Anthropic Docs: docs.anthropic.com
- Claude Agent SDK: github.com/anthropics/claude-code
- MCP Protocol: modelcontextprotocol.io
- Google AI Studio: aistudio.google.com

### Automation
- Make.com (webhook automation)
- n8n (self-hosted automation)
- GitHub Actions (CI/CD for skill deployment)

### Stay Updated
- Follow @AnthropicAI on Twitter for Claude updates
- Follow @GoogleAI for Gemini updates
- Check HuggingFace trending models weekly
- Monitor OpenRouter for new model releases

### Local Models (Free, Private)
Run on your VM with Ollama:
```bash
# Already installed on your VM
ollama list  # see available models
ollama pull llama3.1:8b  # good for quick tasks
ollama pull codellama:13b  # for code generation
ollama pull mistral:7b  # fast general purpose

# Use for free, unlimited tasks
curl http://localhost:11434/api/generate -d '{
  "model": "llama3.1:8b",
  "prompt": "improve this marketing copy: ...",
  "stream": false
}'
```

---

## PART 6: SELF-IMPROVEMENT MEMORY

After each upgrade, log what changed in `~/.openclaw/memory/upgrades.json`:
```json
{
  "upgrades": [
    {
      "date": "2026-04-05",
      "skill": "lead-hunter",
      "change": "Added automated lead scoring with Python script",
      "before_pct": 75,
      "after_pct": 88,
      "result": "Found 3 leads in first automated run",
      "model_used": "Claude Sonnet 4.6"
    }
  ],
  "total_upgrades": 1,
  "avg_improvement": "+13%"
}
```

---

## Error Handling
| Error | Fix |
|-------|-----|
| Claude API rate limited | Switch to Gemini or Ollama local |
| Gemini API key expired | Refresh in Google AI Studio |
| Ollama model not loaded | `ollama pull [model]` then retry |
| Skill rewrite breaks something | Keep backup before rewriting: `cp skill.md skill.md.bak` |
| Boss rejects improvement | Revert and ask Boss what they prefer |
| Upgrade doesn't improve metrics | Roll back, analyze why, try different approach |
| Can't determine what to improve | Look at scorecards — the lowest number is your answer |

## Rules
1. **Never stop improving** — stagnation = death for an AI agent
2. **Measure everything** — if you can't measure improvement, you didn't improve
3. **Back up before changing** — always keep the old version
4. **Test before deploying** — don't push broken skills
5. **Learn from Boss's corrections** — those are the highest-value signals
6. **Steal ideas from the best** — study what top marketing agencies do
7. **Automate the boring parts** — your brain should focus on strategy, not repetition
8. **Ask for help** — use Claude, Gemini, or Ollama when stuck. Never spin your wheels.

## Output Format
```
SELF-UPGRADE COMPLETE:
- Skills upgraded: [count]
- New capabilities: [list]
- Model used: [Claude/Gemini/Ollama]
- Time spent: [minutes]
- Expected impact: [prediction]
- Dashboard updated: [yes/no]
- Next upgrade target: [skill/capability]
```
