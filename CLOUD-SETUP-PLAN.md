# Black Layers AI Marketing Agent — Cloud Setup Plan

## Current Live System (April 1, 2026)

### Google Cloud VM
| Field | Value |
|-------|-------|
| Project | `BlackLayersAI` (ID: `blacklayersai`) |
| VM Name | `blacklayers-agent` |
| IP | `34.132.116.116` |
| Machine | `e2-medium` (2 vCPU, 4GB RAM) |
| Disk | 100GB SSD |
| OS | Ubuntu 22.04 LTS |
| OpenClaw | v2026.3.31 |
| Agent Name | **BLAI (BlackLayer AI)** |
| Gateway | Running (systemd, auto-restarts on reboot) |
| WhatsApp | Connected (+212641503230) |
| Skills | 10 custom skills installed |
| Ollama on VM | Running (qwen2.5:14b, glm-4.7-flash, qwen2.5:7b) — auto-starts on boot |
| Cost | **$0** (using $300 free credits) |

### Your Mac (Local Backup)
| Field | Value |
|-------|-------|
| Machine | MacBook Pro M3 Pro, 18GB RAM |
| Ollama | Installed (v0.19.0) |
| Model | Qwen 2.5 14B (9GB, downloaded) |
| Status | Sleeping — only runs when needed |

---

## How BLAI Works — The Complete Flow

```
You/Brother/Wife send WhatsApp message
            │
            ▼
    ┌───────────────────┐
    │  Google Cloud VM   │
    │  (24/7, always on) │
    └───────┬───────────┘
            │
            ▼
    Try Gemini 3.1 Pro ──── Works? ──── ✅ Respond instantly
            │
            │ Rate limited?
            ▼
    Try Gemini 2.5 Flash ── Works? ──── ✅ Respond instantly
            │
            │ Rate limited?
            ▼
    Try Gemini 2.0 Flash ── Works? ──── ✅ Respond instantly
            │
            │ ALL 3 rate limited? (very rare)
            ▼
    Try Ollama on VM ─────── Works? ──── ✅ Respond (CPU, slower)
    (qwen2.5:14b)            │               Send notification:
                             │               "⚡ Using VM Ollama"
                             │
                             │ VM Ollama busy/failed?
                             ▼
    ┌─────────────────────────────────────────────┐
    │  Is Abdul's Mac online? (via Tailscale)      │
    │                                              │
    │  YES → Route to Mac's Ollama (Qwen 14B)     │
    │         Respond via GPU, unlimited, fast     │
    │         Send notification: "⚡ Using local   │
    │         GPU (Qwen 2.5 14B) — Gemini limit"  │
    │                                              │
    │  NO  → Send message to everyone:             │
    │         "⏳ Rate limit hit. Mac is offline.   │
    │         Retrying in 60 seconds..."           │
    │         Then auto-retry after 60 sec         │
    └─────────────────────────────────────────────┘
```

---

## Who Can Use BLAI (WhatsApp)

| Number | Person | Access |
|--------|--------|--------|
| +212641503230 | Abdul (Owner) | Full control — can change strategy, approve content, give any instruction |
| +923324577459 | Team member | Can ask questions, request content, get reports |
| +14373310603 | Team member | Can ask questions, request content, get reports |
| +212689063416 | Team member | Can ask questions, request content, get reports |

### What Everyone Sees

When the AI model changes (due to rate limits or switching to local GPU), **everyone in the chat gets notified**:

```
🔄 MODEL SWITCH NOTIFICATION

Previous: Gemini 3.1 Pro (Google Cloud)
Now using: Gemini 2.5 Flash (Google Cloud)
Reason: Rate limit on primary model
Speed: Still instant ⚡

Note: All responses are still high quality.
The fallback model is equally capable.
```

Or if it switches to local Mac:
```
🔄 MODEL SWITCH NOTIFICATION

Previous: Gemini (Google Cloud)
Now using: Qwen 2.5 14B (Abdul's Mac — Local GPU)
Reason: All Gemini models rate-limited
Speed: Fast (Apple M3 Pro GPU) ⚡

Note: Running on local hardware.
Unlimited responses. No rate limits.
```

Or if Mac is offline:
```
⏳ TEMPORARY PAUSE

All cloud models are rate-limited and local Mac is offline.
I'll automatically retry in 60 seconds.
Your message is queued — you won't lose it.

Tip: This usually resolves within 1-2 minutes.
```

---

## How Local Mac Fallback Works

### Setup (One-time — already done)
1. Ollama installed on Mac ✅
2. Qwen 2.5 14B downloaded (9GB) ✅
3. Ollama runs on `localhost:11434` when Mac is on

### How Cloud Connects to Mac (When Needed)

**Option A: Tailscale (Recommended — Free)**
Creates a private network between cloud VM and your Mac.

```bash
# On your Mac:
brew install tailscale
tailscale up

# On cloud VM:
tailscale up
# Now VM can reach Mac at its Tailscale IP
```

Once connected, the cloud VM can reach your Mac's Ollama at `http://<mac-tailscale-ip>:11434`. BLAI auto-switches when Gemini is limited.

**Option B: SSH Tunnel**
```bash
# On your Mac (run when you want to enable fallback):
ssh -R 11434:localhost:11434 tonny@34.132.116.116
# This exposes your Mac's Ollama to the cloud VM
```

**Option C: Mac Off = No Fallback**
If your Mac is off, BLAI just retries Gemini after 60 seconds. The 3-model cycle means this is rarely needed.

### When Does Mac Kick In?
- Only when ALL 3 Gemini models are rate-limited (rare)
- Only when Mac is on and Ollama is running
- BLAI checks Mac availability before routing
- If Mac is off → auto-retry Gemini in 60 sec

### Your Mac Stays Clean
- Ollama only activates when a request comes in
- Uses GPU (Apple Silicon unified memory) — barely touches CPU
- No constant background process
- Close Ollama app anytime to disable fallback

---

## AI Models Explained

### Cloud Models (Google Gemini — Free)

| Model | Role | Speed | Quality | Limit |
|-------|------|-------|---------|-------|
| **Gemini 3.1 Pro Preview** | Primary | Instant | Excellent | 15 req/min |
| **Gemini 2.5 Flash** | Fallback 1 | Instant | Very Good | Separate limit |
| **Gemini 2.0 Flash** | Fallback 2 | Instant | Good | Separate limit |

### Local Model (Your Mac — Unlimited)

| Model | Role | Speed | Quality | Limit |
|-------|------|-------|---------|-------|
| **Qwen 2.5 14B** | GPU Fallback | <1 sec (M3 Pro) | Very Good | **Unlimited** |

### How BLAI Gets Smarter Over Time

BLAI doesn't change its AI model — it gets smarter through **memory**:

```
Week 1: BLAI knows the skills you gave it
         ↓
Week 2: BLAI remembers what content worked best
         Remembers Abdul's preferences and corrections
         ↓
Week 4: BLAI has learned optimal posting times
         Knows which hashtags drive engagement
         Remembers 50+ research topics
         ↓
Week 12: BLAI has months of engagement data
          Knows exactly what content your audience likes
          Has a database of leads and their status
          Understands Abdul's communication style perfectly
          ↓
Week 52: BLAI is an expert in your business
          Years of memory, patterns, and intelligence
          Irreplaceable knowledge base
```

The skills (files) stay the same. The memory (learned data) grows every day. This is how BLAI improves without changing the AI model.

---

## BLAI's 10 Skills

| # | Skill | What It Does |
|---|-------|-------------|
| 1 | **master-brain** | Core intelligence — coordinates everything, listens on WhatsApp, learns daily |
| 2 | **brand-identity** | Company DNA — voice, portfolio, messaging, target audience |
| 3 | **twitter-manager** | Creates 3 daily tweets, engages with dev community |
| 4 | **linkedin-manager** | Creates daily professional posts, B2B lead generation |
| 5 | **content-engine** | Writes blogs, YouTube scripts, captions, Quora, Reddit, emails |
| 6 | **video-creator** | Auto-generates videos with AI voiceover + screenshots |
| 7 | **image-creator** | Creates social media graphics via Canva + ImageMagick |
| 8 | **analytics-reporter** | Tracks all platforms, sends daily/weekly WhatsApp reports |
| 9 | **lead-hunter** | Finds clients on Reddit, Twitter, Product Hunt, Fiverr |
| 10 | **self-improver** | Reviews performance, adjusts strategy weekly, runs experiments |

---

## Daily Schedule (BLAI Does Automatically)

| Time (Morocco) | What BLAI Does |
|----------------|---------------|
| 8:00 AM | Create content: 3 tweets + 1 LinkedIn post → send to Abdul |
| 10:00 AM | Answer 2 Quora questions, comment on 3 Reddit threads |
| 12:00 PM | Hunt for leads → send lead report to Abdul |
| 2:00 PM | Post afternoon content with images |
| 5:00 PM | Respond to all comments and mentions |
| 8:00 PM | Send daily report to everyone on WhatsApp |
| 10:00 PM | Self-improvement: analyze what worked, update memory |

---

## Cost Summary

| Item | Monthly Cost |
|------|-------------|
| Google Cloud VM (e2-medium) | $0 (free credits, 12 months) |
| Gemini API | $0 (free tier) |
| OpenClaw | $0 (open source) |
| Ollama on Mac | $0 (open source) |
| Social media accounts | $0 (all free) |
| **TOTAL** | **$0** |

After free credits expire (Month 13+): **~$25/month**

---

## Future Upgrades Path

| When | What | Cost |
|------|------|------|
| **Now** | Gemini free + Mac Qwen fallback | $0 |
| **When profitable** | Buy Mac Mini M4 — dedicated AI server at home | ~$600 |
| **Growing** | Upgrade to Mac Studio M4 — run 70B+ models | ~$2,000-4,000 |
| **Scaled** | Full independence — no cloud, no APIs, everything local | $0/month |

---

## Server Management Commands

### Check BLAI status
```bash
gcloud compute ssh blacklayers-agent --zone=us-central1-a --project=blacklayersai
export PATH=/home/tonny/.npm-global/bin:$PATH
openclaw status
```

### Restart BLAI
```bash
systemctl --user restart openclaw-gateway
```

### View logs
```bash
openclaw logs --follow
```

### Update OpenClaw
```bash
openclaw update --yes
```

### Re-connect WhatsApp (if disconnected)
```bash
openclaw channels login --channel whatsapp --verbose
# Scan QR code with phone
```

### Update skills
```bash
cd ~/blacklayers && git pull
cp ~/blacklayers/openclaw-skills/*.md ~/.openclaw/skills/
systemctl --user restart openclaw-gateway
```

---

*Last updated: April 1, 2026*
*System: Google Cloud + OpenClaw v2026.3.31 + Gemini (3 models) + Mac Qwen 14B fallback*
*Agent: BLAI (BlackLayer AI)*
*Status: LIVE and running 24/7*
