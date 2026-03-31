# Black Layers AI Marketing Agent — Cloud Setup Plan

## Current Verified Google Cloud State

Verified from the Google Cloud CLI on `2026-03-31` without creating any resources:

| Field | Value |
|-------|-------|
| Project Name | `BlackLayersAI` |
| Project ID | `blacklayersai` |
| Project Number | `733441966639` |
| Lifecycle State | `ACTIVE` |
| Create Time | `2026-03-31T14:34:48.672Z` |
| Active CLI Account | `nextgen.hafeez@gmail.com` |

### Already Enabled APIs

- `bigquery.googleapis.com`
- `logging.googleapis.com`
- `monitoring.googleapis.com`
- `storage.googleapis.com`
- related BigQuery and storage support services

### Not Yet Enabled For This Plan

- `compute.googleapis.com` is not enabled yet
- no VM has been created yet
- no cloud disk layout for OpenClaw has been provisioned yet

> This document is now aligned to the real existing project `blacklayersai`. It does **not** mean the setup has been executed.

## The Big Picture

```
┌──────────────────────────────────────────────────────────┐
│                    GOOGLE CLOUD VM                        │
│                   (runs 24/7, never sleeps)                │
│                                                          │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────────┐ │
│  │  OpenClaw    │  │  Headless     │  │  AI Content      │ │
│  │  Gateway     │  │  Chrome       │  │  Generator       │ │
│  │  (brain)     │  │  (browser)    │  │  (images/video)  │ │
│  └──────┬──────┘  └──────┬───────┘  └────────┬─────────┘ │
│         │                │                    │           │
│         └────────────────┼────────────────────┘           │
│                          │                                │
│              ┌───────────┴───────────┐                    │
│              │   Skill Files &       │                    │
│              │   Memory Storage      │                    │
│              │   (Google Cloud Disk)  │                    │
│              └───────────────────────┘                    │
│                                                          │
└────────────────────────┬─────────────────────────────────┘
                         │
            ┌────────────┼────────────────┐
            │            │                │
      ┌─────┴─────┐ ┌───┴────┐  ┌───────┴───────┐
      │ WhatsApp   │ │Twitter │  │ LinkedIn      │
      │ (to you)   │ │ X.com  │  │ Instagram     │
      │            │ │        │  │ Reddit/Quora  │
      └───────────┘ └────────┘  └───────────────┘
```

---

## What You Need on Google Cloud

### Recommended VM Spec

| Resource | Spec | Why |
|----------|------|-----|
| Machine Type | `e2-standard-4` (4 vCPU, 16 GB RAM) | Runs OpenClaw + Chrome + AI tools smoothly |
| Disk | 100 GB SSD | Stores skills, memory, generated images/videos |
| OS | Ubuntu 22.04 LTS | Stable, well-supported |
| GPU | **NOT needed** | OpenClaw uses cloud AI APIs (Claude/GPT), not local models |
| Region | `us-central1` | Cheapest, good connectivity |

### Estimated Cost

| Tier | Spec | Monthly Cost |
|------|------|-------------|
| **Budget** | `e2-medium` (2 vCPU, 4 GB) | ~$25/month |
| **Recommended** | `e2-standard-4` (4 vCPU, 16 GB) | ~$50/month |
| **Power** | `e2-standard-8` (8 vCPU, 32 GB) | ~$100/month |

**Start with Budget ($25/month).** Upgrade later if needed.

> Google Cloud gives **$300 free credits** for new accounts — that's 12 months free on the budget tier.

---

## Complete Setup Steps

### Phase 1: Create Google Cloud VM (Day 1)

```bash
# 1. Use the existing project:
#    Project name: BlackLayersAI
#    Project ID: blacklayersai
#    Project number: 733441966639
#
# 2. Set the active project in gcloud
gcloud config set project blacklayersai
#
# 3. Enable APIs needed for VM-based execution
#    (serviceusage is usually already available, but keep it here for a clean runbook)
gcloud services enable compute.googleapis.com
#
# 4. Create VM instance with these settings:

gcloud compute instances create blacklayers-agent \
  --machine-type=e2-medium \
  --zone=us-central1-a \
  --image-family=ubuntu-2204-lts \
  --image-project=ubuntu-os-cloud \
  --boot-disk-size=100GB \
  --boot-disk-type=pd-ssd \
  --tags=http-server,https-server
```

### Phase 1.5: Recommended Project Hygiene Before Provisioning

These are not blockers for experimentation, but they should be done before production use:

```bash
# Add an environment tag later when you are ready to standardize the project
# Example values: Production, Development, Test, Staging
#
# Also confirm billing is attached before creating the VM.
```

Notes:
- During CLI verification, Google Cloud warned that the project does not yet have an `environment` tag.
- Since `compute.googleapis.com` is not currently enabled, VM creation will fail until that API is enabled.
- Logging and Monitoring are already enabled, which is good for later health checks and reporting.

### Phase 2: Install Everything on the VM (Day 1)

SSH into the VM and run:

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Node.js 20
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs

# Install Chrome (headless browser for OpenClaw)
wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" | sudo tee /etc/apt/sources.list.d/google-chrome.list
sudo apt update && sudo apt install -y google-chrome-stable

# Install FFmpeg (for video creation)
sudo apt install -y ffmpeg

# Install ImageMagick (for image creation)
sudo apt install -y imagemagick

# Install Python + AI image/video tools
sudo apt install -y python3-pip python3-venv
pip3 install Pillow moviepy edge-tts

# Install OpenClaw
npm install -g openclaw

# Install PM2 (keeps OpenClaw running 24/7, auto-restarts)
npm install -g pm2
```

### Phase 3: Install Custom Skills (Day 1)

```bash
# Create skills directory
mkdir -p ~/.openclaw/skills

# Clone your repo with the skills
git clone https://github.com/nextgenhafeez/skills-introduction-to-github.git ~/blacklayers

# Copy skills
cp ~/blacklayers/openclaw-skills/*.md ~/.openclaw/skills/
```

### Phase 4: Start OpenClaw 24/7 (Day 1)

```bash
# Start OpenClaw with PM2 (auto-restarts, runs forever)
pm2 start "openclaw" --name blacklayers-agent

# Make it survive reboots
pm2 startup
pm2 save

# Check status anytime
pm2 status
pm2 logs blacklayers-agent
```

### Phase 5: Connect WhatsApp (Day 1)

Follow OpenClaw's WhatsApp setup. Once connected:
- OpenClaw runs on Google Cloud 24/7
- You talk to it from your phone via WhatsApp
- It posts, creates, engages — all from the cloud
- Your Mac stays untouched

---

## AI Content Creation Tools (Free)

OpenClaw on the cloud VM can use these free tools to create content:

### Images

| Tool | What It Does | Cost |
|------|-------------|------|
| **Canva API** (via browser) | Create social media graphics | Free tier |
| **ImageMagick** | Generate text-based graphics, banners | Free (installed) |
| **Unsplash API** | Get free stock photos | Free |
| **Carbon.now.sh** (via browser) | Beautiful code screenshots for dev posts | Free |

### Videos

| Tool | What It Does | Cost |
|------|-------------|------|
| **FFmpeg** | Combine images + audio into videos | Free (installed) |
| **Edge-TTS** | AI text-to-speech (Microsoft voices) | Free |
| **MoviePy** | Python video editing/creation | Free (installed) |

### Content Flow for Auto-Generated Videos

```
1. OpenClaw writes script (using content-engine skill)
2. Edge-TTS converts script to voiceover audio
3. OpenClaw generates/collects images (app screenshots, stock photos)
4. FFmpeg/MoviePy combines images + audio into video
5. OpenClaw uploads to YouTube via browser automation
6. OpenClaw sends you WhatsApp notification: "New video uploaded ✓"
```

### Content Flow for Auto-Generated Images

```
1. OpenClaw writes post text (using twitter/linkedin skill)
2. OpenClaw opens Canva in browser, uses template
3. Fills in text, adjusts colors to brand (black/white/blue)
4. Downloads the image
5. Posts image + caption to Instagram/Twitter/LinkedIn
6. Reports to you on WhatsApp
```

---

## Enhanced Skills for Cloud (New)

### SKILL-video-creator.md
Creates YouTube Shorts, Reels, and TikTok videos automatically:
- Writes script from content-engine
- Generates AI voiceover with Edge-TTS
- Combines with app screenshots/screen recordings
- Adds background music (royalty-free)
- Uploads to YouTube, sends you notification

### SKILL-image-creator.md
Creates social media graphics automatically:
- Uses Canva browser automation OR ImageMagick
- Creates quote cards, app showcases, infographics
- Follows brand colors (black, white, blue)
- Sizes for each platform (Twitter 1200x675, Instagram 1080x1080, LinkedIn 1200x627)

### SKILL-analytics-reporter.md
Tracks performance and sends you reports:
- Checks follower counts on each platform
- Tracks post engagement (likes, comments, shares)
- Identifies top-performing content
- Suggests what to post more of
- Sends weekly report on WhatsApp every Friday

### SKILL-lead-hunter.md
Finds potential clients automatically:
- Searches Product Hunt for new startups without apps
- Monitors Reddit/Twitter for "looking for app developer"
- Checks Fiverr for new relevant buyer requests
- Drafts personalized outreach for each lead
- Sends lead list to you on WhatsApp daily

### SKILL-self-improver.md
Makes OpenClaw smarter over time:
- Tracks which posts get the most engagement
- Learns what content style works best
- Adjusts posting times based on engagement data
- A/B tests different post formats
- Updates its own strategy weekly
- Sends you improvement report: "This week I learned..."

---

## Memory & Data Storage

Everything saves to the Google Cloud VM disk (persists across restarts):

```
~/.openclaw/
├── skills/                    # All skill files
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
├── memory/                    # OpenClaw's persistent memory
│   ├── brand-knowledge.json
│   ├── posting-history.json
│   ├── engagement-data.json
│   ├── leads-database.json
│   └── learning-log.json
└── content/                   # Generated content archive
    ├── images/
    ├── videos/
    ├── blog-posts/
    └── scripts/
```

### Backup to Google Cloud Storage (Optional)

```bash
# Daily backup cron job
0 2 * * * gsutil -m rsync -r ~/.openclaw gs://blacklayers-agent-backup/
```

---

## Daily Lifecycle (What Happens Every 24 Hours)

```
6:00 AM  — OpenClaw wakes up, checks trending topics
7:00 AM  — Generates today's content (3 tweets, 1 LinkedIn, 1 Instagram)
8:00 AM  — Posts morning tweet
8:30 AM  — Creates image for Instagram post
9:00 AM  — Posts LinkedIn update
10:00 AM — Answers 2 Quora questions
11:00 AM — Comments on 3 Reddit threads
12:00 PM — Hunts for leads (Product Hunt, Reddit, Twitter)
2:00 PM  — Posts afternoon tweet with app showcase image
3:00 PM  — Sends Instagram post draft to Abdul on WhatsApp
4:00 PM  — Engages with comments/mentions on all platforms
5:00 PM  — Creates tomorrow's content drafts
6:00 PM  — Posts evening engagement tweet
7:00 PM  — Checks analytics (follower growth, engagement)
8:00 PM  — Sends Abdul daily WhatsApp report
9:00 PM  — Saves learning data (what worked, what didn't)
```

### Weekly Lifecycle

```
Monday    — Write & publish blog post, create 2 images
Tuesday   — Write YouTube script, send to Abdul
Wednesday — Create short video (automated), hunt 5 leads
Thursday  — Send 10 cold emails, create infographic
Friday    — Weekly analytics report to Abdul on WhatsApp
Saturday  — Abdul records YouTube video (script ready)
Sunday    — OpenClaw reviews week's data, updates strategy
```

---

## Your Daily Routine (Phone Only)

| Time | What You Do | Where |
|------|------------|-------|
| Morning | Read OpenClaw's overnight summary | WhatsApp |
| Afternoon | Approve any flagged content | WhatsApp |
| Evening | Read daily report, reply to hot leads | WhatsApp |
| Saturday | Record 1 YouTube video (script on WhatsApp) | Phone camera |

**Total time: 15 min/day + 30 min on Saturday**

---

## Setup Timeline

| Day | Task | Who Does It |
|-----|------|------------|
| Day 1 | Create Google Cloud VM, install everything | Claude Code guides you |
| Day 1 | Install OpenClaw + skills on VM | Claude Code guides you |
| Day 1 | Connect WhatsApp to cloud OpenClaw | You (follow guide) |
| Day 2 | Create social media accounts | You (one-time, 30 min) |
| Day 2 | Log into each platform via OpenClaw browser | You (one-time, 10 min) |
| Day 3 | Start autopilot, OpenClaw begins posting | OpenClaw |
| Day 7 | First weekly report | OpenClaw → WhatsApp |
| Day 30 | First monthly review | OpenClaw → WhatsApp |

---

## Cost Summary

| Item | Monthly Cost |
|------|-------------|
| Google Cloud VM (e2-medium) | $25 (FREE first 12 months with $300 credit) |
| OpenClaw | Free (open source) |
| Claude/GPT API (for content) | ~$5-10 (or use free tiers) |
| All social media accounts | Free |
| Domain (blacklayers.ca) | Already have it |
| **Total Year 1** | **$0 (using Google credits)** |
| **Total Year 2+** | **~$30-35/month** |

---

## What Makes This Special

| Traditional Digital Marketing | Your Setup |
|------------------------------|-----------|
| Hire a marketer: $3,000-5,000/month | OpenClaw: $25/month |
| They work 8 hours/day | OpenClaw works 24/7 |
| They take vacations | OpenClaw never stops |
| They forget brand voice | OpenClaw has perfect memory |
| They manage 2-3 platforms | OpenClaw manages ALL platforms |
| They create content manually | OpenClaw auto-generates everything |
| They send reports when asked | OpenClaw reports daily on WhatsApp |

---

## Next Steps

1. **Create Google Cloud account** → console.cloud.google.com (get $300 free credits)
2. **Tell Claude Code to set up the VM** → I'll give you exact commands
3. **Create social media accounts** (YouTube, Twitter, Instagram, LinkedIn, Reddit)
4. **Connect WhatsApp to OpenClaw on the cloud**
5. **Send the autopilot message**
6. **Check WhatsApp daily — OpenClaw handles the rest**

---

*Plan created: March 31, 2026*
*Architecture: Google Cloud + OpenClaw + Browser Automation + AI Content Generation*
*Total cost: $0 for first year*
*Your time: 15 min/day on WhatsApp*
