# BLAI v2 — Status & Architecture

**Last updated:** 2026-04-10

## Overview

BLAI (Black Layers AI) is Abdul Hafeez's WhatsApp business assistant running 24/7 on Google Cloud VM. Built on Baileys (WhatsApp Web protocol) with multi-LLM brain (Gemini + Groq fallback) and Make.com integration for real social media posting and lead hunting.

## Architecture

```
WhatsApp -> Baileys (Node.js) -> bridge.py -> brain.py
                                                 |
                                    +------------+------------+
                                    |                         |
                              Gemini API                  Groq API
                              (7 keys)                    (4 keys)
                                    |                         |
                                    +------------+------------+
                                                 |
                                          [skill_router]
                                                 |
                              +------------------+------------------+
                              |                                     |
                       Real Skills                          Make.com Webhooks
                       (Python)                             (5 platforms)
                       - lead_hunter_real                    - YouTube + Buffer
                       - email_outreach                      - Twitter (via Buffer)
                       - social_poster_real                  - TikTok (via Buffer)
                       - make_com (API client)               - Facebook
                                                             - Instagram
```

## API Keys (11 total)

| Provider | Keys | Model | Daily Limit | Total Capacity |
|----------|------|-------|-------------|----------------|
| Google Gemini | 7 | gemini-2.5-flash | 1,500 req/day/key | 10,500 req/day |
| Groq | 4 | llama-3.1-8b-instant | 14,400 req/day/key | 57,600 req/day |
| **Total** | **11** | | | **~68,100 req/day** |

**Auto-failover:** When all Gemini keys hit 429, brain caches the block for 1 hour and routes all requests to Groq. Switches back automatically when Gemini quota resets.

## Memory System

- **People memory** (`memory/people/`): Boss, family, clients with profiles
- **Conversation history**: 8 messages per phone (rolling window, optimized for token usage)
- **Identity** (`config/identity.json`): Boss info, family, clients, services
- **Knowledge** (`config/knowledge.json`): Lessons learned, corrections, infrastructure
- **Preferences** (`memory/preferences.json`): Boss corrections and likes

## Skills Deployed

| Skill | Function | Status |
|-------|----------|--------|
| `make_com.py` | Make.com API client (scenarios, webhooks) | Ready |
| `lead_hunter_real.py` | Real lead search via Reddit/HackerNews + Make.com | Ready |
| `email_outreach.py` | Email sending via Make.com webhook | Ready |
| `social_poster_real.py` | Multi-platform posting (5 platforms) | Ready |

## Dashboard

Live at: `http://34.123.81.29:8080/blai-command-center.html`

Features:
- Real-time API key status (tests actual generateContent endpoints)
- Per-key status (READY / QUOTA EXCEEDED)
- "Brain using:" indicator (Gemini or Groq fallback)
- Auto-refresh every 60 seconds
- WhatsApp connection uptime
- Make.com platforms ready

## Stability

- **PM2** manages the Node process with 30s restart delay + exponential backoff
- **Watchdog script** monitors `.health` file, force-restarts if silent for 2min
- **Message dedup** prevents reprocessing
- **Stale message filter** drops messages older than 30s (prevents quota waste on old queue)
- **5s stabilization window** after connect before processing messages

## Known Issues

1. **440 disconnect cycles**: WhatsApp drops connection every 3-5 messages. PM2 auto-restarts within 30s. Investigating Baileys library alternatives.
2. **Gemini quota timezone**: Resets at 8:00 AM Morocco time daily.

## Quota Fallback

When ALL 11 API keys are exhausted, BLAI sends a multilingual professional maintenance message in 5 languages:
- English
- French
- German
- Urdu
- Arabic

With reset time in Morocco timezone and contact info (info@blacklayers.ca).

## Next Session Priorities

1. Fix 440 disconnect permanently (try alternate WhatsApp library)
2. Build Kling AI video generation skill
3. Make.com lead hunting workflow
4. Dashboard logo fix
