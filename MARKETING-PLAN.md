# Black Layers — AI Agent Marketing Plan

## Goal
One AI agent runs the entire Black Layers digital marketing.
It posts, creates content, finds clients, researches, learns, and reports — all automatically.
Abdul talks to it on WhatsApp. That's it.

**Total cost: $0 first year (Google Cloud free credits)**
**Abdul's time: 15 min/day on WhatsApp**

---

## The Agent — 10 Custom Skills

### The Brain
| Skill | What It Does |
|-------|-------------|
| **master-brain** | Central intelligence — coordinates all skills, listens on WhatsApp, researches anything Abdul asks, learns every day, gets smarter every week |

### Knowledge
| Skill | What It Does |
|-------|-------------|
| **brand-identity** | Everything about Black Layers — voice, portfolio, audience, key messages, visual brand |

### Content Creation
| Skill | What It Does |
|-------|-------------|
| **content-engine** | Writes blog posts, YouTube scripts, Instagram captions, Quora answers, Reddit comments, cold emails |
| **video-creator** | Auto-generates YouTube Shorts, Reels, TikToks using AI voiceover (Edge-TTS) + screenshots + FFmpeg |
| **image-creator** | Creates social media graphics via Canva browser automation + ImageMagick |

### Social Media
| Skill | What It Does |
|-------|-------------|
| **twitter-manager** | Creates and posts 3 daily tweets, engages with dev community, replies to mentions |
| **linkedin-manager** | Creates daily professional posts, engages with connections, generates B2B leads |

### Business Growth
| Skill | What It Does |
|-------|-------------|
| **lead-hunter** | Finds potential clients on Reddit, Twitter, Product Hunt, Fiverr — sends leads to Abdul on WhatsApp |
| **analytics-reporter** | Tracks all platforms, sends daily + weekly performance reports on WhatsApp |
| **self-improver** | Reviews what worked and what didn't, adjusts strategy weekly, runs experiments, gets smarter |

---

## How Abdul Uses It (WhatsApp Only)

Just message naturally. The agent understands everything:

| You Say | Agent Does |
|---------|-----------|
| "What did you do today?" | Shows all posts, engagement, leads found |
| "Search about latest iOS 20 features" | Researches 5+ sources, sends summary |
| "Post something about AdClose" | Creates and posts across platforms |
| "Find me clients who need apps" | Hunts leads on Reddit, Twitter, Product Hunt |
| "How are our social numbers?" | Sends full analytics report |
| "Learn about Flutter" | Researches deeply, saves to memory |
| "Write a blog about app development costs" | Drafts full article, sends for review |
| "Create a video about Sakeena" | Generates video with AI voiceover |
| "Stop posting on Reddit" | Adjusts immediately |
| "Focus more on LinkedIn" | Shifts strategy right away |
| "What's trending in AI?" | Searches web, summarizes key trends |
| "Improve our content strategy" | Analyzes data, proposes changes |

**The agent also messages YOU proactively:**
- Morning: daily plan
- Found a hot lead: instant alert
- Interesting news: "Hey Abdul, Apple just announced..."
- Evening: daily report with numbers

---

## Daily Autopilot Schedule

The agent runs this every day without being told:

| Time | What Happens |
|------|-------------|
| 6:00 AM | Checks trending topics in tech |
| 7:00 AM | Creates today's content (tweets, LinkedIn post, captions) |
| 8:00 AM | Posts morning tweet |
| 9:00 AM | Posts LinkedIn update |
| 10:00 AM | Answers 2 Quora questions |
| 11:00 AM | Comments on 3 Reddit threads |
| 12:00 PM | Hunts leads, sends lead report to Abdul |
| 2:00 PM | Posts afternoon tweet with image |
| 3:00 PM | Sends Instagram draft to Abdul for approval |
| 5:00 PM | Responds to all comments and mentions |
| 6:00 PM | Posts evening engagement tweet |
| 8:00 PM | Sends daily report to Abdul on WhatsApp |
| 10:00 PM | Reviews today's performance, learns, updates strategy |

## Weekly Schedule

| Day | Extra Tasks |
|-----|------------|
| Monday | Write + publish blog post |
| Tuesday | Draft 5 cold outreach emails |
| Wednesday | Write YouTube script, send to Abdul |
| Thursday | Draft 5 more outreach emails |
| Friday | Send weekly performance report |
| Saturday | Abdul records YouTube video (script provided) |
| Sunday | Self-improvement: review week, adjust strategy, learn new topic |

---

## Setup Steps

### Step 1: Google Cloud VM
```bash
# Create VM (e2-medium, $25/month, FREE first year with $300 credits)
gcloud compute instances create blacklayers-agent \
  --machine-type=e2-medium \
  --zone=us-central1-a \
  --image-family=ubuntu-2204-lts \
  --image-project=ubuntu-os-cloud \
  --boot-disk-size=100GB \
  --boot-disk-type=pd-ssd
```

### Step 2: Install Everything on VM
```bash
# System
sudo apt update && sudo apt upgrade -y

# Node.js
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs

# Chrome (for browser automation)
wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" | sudo tee /etc/apt/sources.list.d/google-chrome.list
sudo apt update && sudo apt install -y google-chrome-stable

# Media tools (video + image creation)
sudo apt install -y ffmpeg imagemagick python3-pip
pip3 install Pillow moviepy edge-tts

# OpenClaw
npm install -g openclaw

# PM2 (keeps agent running 24/7)
npm install -g pm2
```

### Step 3: Install Skills
```bash
# Clone repo
git clone https://github.com/nextgenhafeez/skills-introduction-to-github.git ~/blacklayers

# Copy all 10 skills
mkdir -p ~/.openclaw/skills
cp ~/blacklayers/openclaw-skills/*.md ~/.openclaw/skills/
```

### Step 4: Start Agent 24/7
```bash
pm2 start "openclaw" --name blacklayers-agent
pm2 startup && pm2 save
```

### Step 5: Connect WhatsApp
Follow OpenClaw WhatsApp setup. Once connected, send:

> You are my personal AI agent. Read all skills in your skills folder.
> Start your daily marketing routine for Black Layers immediately.
> Post on all platforms daily. Search and learn when I ask.
> Send me daily reports at 8 PM. Improve yourself every week.
> Start now.

### Step 6: Create Social Media Accounts (One-Time)
| Platform | Cost |
|----------|------|
| YouTube — "Black Layers" | Free |
| Twitter/X — @blacklayers | Free |
| Instagram — @blacklayers.ca | Free |
| LinkedIn — Company Page | Free |
| Reddit — u/blacklayers | Free |
| Quora — Black Layers | Free |
| Medium — Black Layers blog | Free |
| Dev.to — blacklayers | Free |
| Google Business | Free |
| Google Search Console | Free |

Log into each platform once through OpenClaw's browser. It saves the session.

---

## Memory & Storage (Google Cloud Disk)

```
~/.openclaw/
├── skills/                    # 10 skill files (the agent's knowledge)
│   ├── SKILL-master-brain.md
│   ├── SKILL-brand-identity.md
│   ├── SKILL-twitter-manager.md
│   ├── SKILL-linkedin-manager.md
│   ├── SKILL-content-engine.md
│   ├── SKILL-video-creator.md
│   ├── SKILL-image-creator.md
│   ├── SKILL-analytics-reporter.md
│   ├── SKILL-lead-hunter.md
│   └── SKILL-self-improver.md
├── memory/                    # Agent's brain (learns over time)
│   ├── daily-log.json
│   ├── learning-log.json
│   ├── abdul-preferences.json
│   ├── research-archive.json
│   ├── engagement-data.json
│   ├── leads-database.json
│   └── content-history.json
└── content/                   # Generated content
    ├── images/
    ├── videos/
    ├── blog-posts/
    └── scripts/
```

**100% portable** — move to your Mac, AWS, or Alibaba anytime with one backup command:
```bash
tar -czf openclaw-backup.tar.gz ~/.openclaw/
```

---

## Growth Targets

| Timeline | Followers | Leads | Revenue |
|----------|-----------|-------|---------|
| Month 1 | 500 total | 2-3 inquiries | — |
| Month 3 | 2,000 total | 5-10/month | First inbound client |
| Month 6 | 5,000 total | 15-20/month | 2-3 clients/month |
| Month 12 | 15,000 total | 30+/month | Consistent inbound |

---

## Cost Summary

| Item | Cost |
|------|------|
| Google Cloud VM | $0 first year ($300 free credits) |
| OpenClaw | Free (open source) |
| All social media accounts | Free |
| AI content creation tools | Free (Edge-TTS, FFmpeg, ImageMagick) |
| **Total Year 1** | **$0** |
| **Total Year 2+** | **~$25-35/month** |

---

## vs Hiring a Human

| | Human Marketer | Your AI Agent |
|--|---------------|--------------|
| Cost | $3,000-5,000/month | $25/month |
| Hours | 8 hrs/day, weekdays | 24/7/365 |
| Platforms | 2-3 max | All platforms |
| Speed | Creates 2-3 posts/day | Creates 10+ posts/day |
| Learning | Slow, needs training | Improves itself weekly |
| Reporting | When asked | Daily + weekly automatic |
| Lead hunting | Manual, limited | Automated, continuous |
| Vacation | Takes time off | Never stops |

---

*Plan created: March 31, 2026*
*Skills: 10 custom OpenClaw skills built by Claude Code*
*Architecture: Google Cloud VM + OpenClaw + WhatsApp*
*Last updated: March 31, 2026*
