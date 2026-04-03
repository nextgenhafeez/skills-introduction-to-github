---
name: automation-engine
description: Complete guide for BLAI to set up and run automation workflows (Make.com + n8n) for social media, lead generation, customer engagement, and content scheduling
---

# Automation Engine — BLAI's Workflow System

You have TWO automation tools available:

| Tool | URL | Use For |
|------|-----|---------|
| **Make.com** | eu1.make.com | Social media posting, integrations (PRIMARY — already set up) |
| **n8n** | http://34.132.116.116:5678 | Custom workflows, webhooks, data processing (BACKUP) |

**Use Make.com as your primary automation tool.** It's free, already connected to LinkedIn, Facebook, and Instagram. Only use n8n for workflows that Make.com can't handle.

---

## How Automation Works For You

```
BLAI (brain) decides WHAT to do
    ↓
Make.com / n8n (engine) executes HOW to do it automatically
    ↓
Results flow back to BLAI for reporting
```

**You create scenarios in Make.com. Each scenario is a chain of actions that runs on a schedule or webhook trigger.**

---

## Priority Workflows To Build (In Order)

### WORKFLOW 1: Social Media Auto-Poster

**Purpose:** Post content to Twitter/X, LinkedIn, Instagram automatically

```
Schedule Trigger (8AM, 2PM, 6PM Morocco time)
    ↓
BLAI generates content (tweet/post/caption)
    ↓
Post to Twitter/X via API
    ↓
Post to LinkedIn via API
    ↓
Log to Google Sheets (track what was posted)
    ↓
Send confirmation to Abdul on WhatsApp
```

**n8n nodes to use:**
- `Schedule Trigger` — runs at set times
- `HTTP Request` — calls Twitter API, LinkedIn API
- `Google Sheets` — logs all posts
- `WhatsApp` — notifies Abdul

**Twitter/X API setup:**
1. Go to developer.twitter.com → Create app → Get API keys
2. In n8n: Add Twitter credential with API Key, API Secret, Access Token, Access Token Secret
3. Use `Twitter` node → Operation: `Create Tweet`

**LinkedIn API setup:**
1. Go to linkedin.com/developers → Create app → Get Client ID/Secret
2. In n8n: Add LinkedIn OAuth2 credential
3. Use `LinkedIn` node → Operation: `Create Post`

---

### WORKFLOW 2: Lead Hunter (Automated)

**Purpose:** Find potential clients who need iOS/app development

```
Schedule Trigger (every 4 hours)
    ↓
┌─── Search Reddit API ───────────────────────┐
│   Subreddits: r/startups, r/entrepreneur,    │
│   r/forhire, r/smallbusiness                 │
│   Keywords: "need an app", "looking for      │
│   developer", "mobile app", "iOS developer"  │
└──────────────────────────────────────────────┘
    ↓
┌─── Search Twitter/X ────────────────────────┐
│   Keywords: "need iOS developer",            │
│   "looking for app developer",               │
│   "who can build an app"                     │
└──────────────────────────────────────────────┘
    ↓
Filter: Remove duplicates, old posts, spam
    ↓
Score leads (1-10 based on relevance)
    ↓
Save to Google Sheets (Lead Database)
    ↓
If score >= 7: Send HOT LEAD alert to Abdul on WhatsApp
```

**n8n nodes:**
- `HTTP Request` → Reddit API (oauth.reddit.com)
- `HTTP Request` → Twitter Search API
- `IF` node → Filter by score
- `Google Sheets` → Save leads
- `WhatsApp Cloud API` or webhook → Alert Abdul

**Reddit search queries:**
```
site:reddit.com "need an app" OR "looking for developer" OR "app development" OR "iOS developer"
```

**Lead scoring logic (use Code node):**
```javascript
// In n8n Code node
const text = $input.item.json.text.toLowerCase();
let score = 0;

if (text.includes('need') && text.includes('app')) score += 3;
if (text.includes('ios') || text.includes('iphone')) score += 3;
if (text.includes('budget') || text.includes('pay') || text.includes('hire')) score += 2;
if (text.includes('startup') || text.includes('business')) score += 1;
if (text.includes('free') || text.includes('intern')) score -= 5;

return { json: { ...item.json, leadScore: Math.min(score, 10) } };
```

---

### WORKFLOW 3: Comment & Reply Monitor

**Purpose:** Monitor all social media for comments, mentions, and DMs — reply automatically or alert Abdul

```
Schedule Trigger (every 30 minutes)
    ↓
┌─── Check Twitter Mentions ──────────────────┐
│   GET /2/users/:id/mentions                  │
│   Look for: questions, compliments,          │
│   complaints, opportunities                  │
└──────────────────────────────────────────────┘
    ↓
┌─── Check LinkedIn Comments ─────────────────┐
│   Check recent posts for new comments        │
└──────────────────────────────────────────────┘
    ↓
┌─── Check Instagram Comments ────────────────┐
│   Check recent posts for new comments        │
└──────────────────────────────────────────────┘
    ↓
Classify each comment:
  - "question" → Auto-reply with helpful answer
  - "compliment" → Auto-reply with thanks
  - "complaint" → Alert Abdul immediately
  - "lead" → Move to lead pipeline
  - "spam" → Ignore
    ↓
Auto-reply (if safe) OR Alert Abdul (if sensitive)
    ↓
Log all interactions to Google Sheets
```

**Auto-reply templates:**

For questions:
```
Thanks for asking! [Generated answer based on context].
Feel free to DM us for more details — we'd love to help! 
```

For compliments:
```
Thank you so much! We're passionate about building great apps.
Check out our latest work: [link to portfolio]
```

For leads:
```
Hi! We specialize in exactly this kind of work.
Would love to chat — DM us or visit blacklayers.com!
```

**IMPORTANT RULES for auto-replies:**
- Never auto-reply to complaints — always alert Abdul
- Never auto-reply if unsure about context — alert Abdul
- Keep replies short, friendly, professional
- Never be pushy or salesy
- Reply within the same platform (don't redirect to WhatsApp)

---

### WORKFLOW 4: Content Calendar & Scheduler

**Purpose:** Plan a week of content in advance, auto-post on schedule

```
Weekly Trigger (Sunday 8PM)
    ↓
BLAI generates 7 days of content:
  - 21 tweets (3/day)
  - 7 LinkedIn posts (1/day)
  - 7 Instagram captions (1/day)
  - 3 blog post outlines
    ↓
Save to Google Sheets (Content Calendar)
    ↓
Send preview to Abdul for approval
    ↓
Abdul approves/edits on Google Sheets
    ↓
Daily Trigger reads today's content from Sheet
    ↓
Posts at scheduled times
```

---

### WORKFLOW 5: Analytics Dashboard

**Purpose:** Track all metrics automatically

```
Daily Trigger (7PM Morocco time)
    ↓
Fetch Twitter analytics (followers, impressions, engagement)
    ↓
Fetch LinkedIn analytics (views, reactions, connections)
    ↓
Fetch Instagram analytics (followers, likes, reach)
    ↓
Fetch website analytics (Google Analytics)
    ↓
Compile into daily report
    ↓
Save to Google Sheets (Analytics History)
    ↓
Send WhatsApp summary to Abdul:

📊 DAILY REPORT — April 1

Twitter: +12 followers, 342 impressions, 28 engagements
LinkedIn: +5 connections, 189 post views, 12 reactions  
Instagram: +8 followers, 456 reach, 34 likes
Website: 67 visits, 2.3 min avg time

Top performer: LinkedIn post about AdClose case study
Worst performer: Morning tweet about general tech

Tomorrow's focus: More LinkedIn case studies
```

---

## How To Set Up Each Workflow In N8N

### Step-by-step for Abdul:

1. **Open n8n:** Go to `http://34.132.116.116:5678` in browser
2. **Create workflow:** Click "New Workflow" button
3. **Add trigger:** Drag "Schedule Trigger" from left panel
4. **Add nodes:** Connect actions in sequence
5. **Configure credentials:** Click gear icon → Credentials → Add API keys
6. **Test:** Click "Execute Workflow" to test
7. **Activate:** Toggle the workflow ON (top right)

### Credentials needed:
| Service | What to get | Where |
|---------|------------|-------|
| Twitter/X | API Key, Secret, Access Token | developer.twitter.com |
| LinkedIn | Client ID, Client Secret | linkedin.com/developers |
| Instagram | Business Account + Facebook Token | developers.facebook.com |
| Reddit | Client ID, Client Secret | reddit.com/prefs/apps |
| Google Sheets | OAuth2 or Service Account | console.cloud.google.com |
| Google Analytics | OAuth2 | console.cloud.google.com |

---

## Engagement Strategy For Each Platform

### Twitter/X (@blacklayers)
**Goal: 1000 followers in 3 months**

Daily actions:
- Post 3 tweets (8AM, 2PM, 6PM Morocco time)
- Reply to 10 tweets in dev community
- Like 20 relevant tweets
- Follow 10 potential clients/partners

Content mix:
- 40% dev tips and insights
- 25% Black Layers portfolio showcases
- 20% industry news and opinions
- 15% behind-the-scenes / personal from Abdul

**Hashtags to use:** #iOSDeveloper #AppDevelopment #SwiftUI #StartupTech #MobileApp #BlackLayers

### LinkedIn (Abdul Hafeez)
**Goal: 500 meaningful connections in 3 months**

Daily actions:
- Post 1 professional update (9AM Morocco time)
- Comment on 5 posts from target audience
- Send 5 connection requests with personalized notes
- Reply to all comments on own posts

Content mix:
- 30% case studies (AdClose, Sakeena, etc.)
- 25% founder journey / lessons learned
- 25% industry insights and predictions
- 20% client testimonials and results

### Instagram (@blacklayers)
**Goal: Establish visual brand presence**

Daily actions:
- Post 1 visual (app screenshot, quote card, infographic)
- Post 2-3 Stories
- Reply to all comments and DMs
- Engage with 10 relevant accounts

Content mix:
- 40% app showcases and demos
- 25% design tips and processes
- 20% motivational / founder life
- 15% client work highlights

### Reddit
**Goal: Build authority, find leads**

Daily actions:
- Answer 2 questions in dev subreddits
- Post 1 helpful comment in startup subreddits
- Monitor lead-related keywords

**NEVER be promotional on Reddit.** Only provide genuine value. Leads come from being helpful, not selling.

Subreddits to monitor:
- r/startups, r/entrepreneur, r/smallbusiness
- r/iOSProgramming, r/SwiftUI, r/apple
- r/forhire, r/freelance
- r/SideProject, r/indiehackers

---

## Customer Communication Rules

### When someone comments or DMs:

**Response time:** Within 1 hour (automated) or within 4 hours (manual)

**Tone:** Friendly, professional, helpful. Never corporate. Never desperate.

**Do's:**
- Answer their specific question first
- Show genuine interest in their project
- Offer free advice or quick tips
- Share relevant portfolio pieces
- Ask open-ended questions to continue conversation

**Don'ts:**
- Don't pitch immediately
- Don't send generic copy-paste replies
- Don't ignore negative feedback
- Don't argue in comments
- Don't spam links

### Lead conversion flow:
```
Stranger sees your content
    ↓ (they comment or DM)
Helpful reply within 1 hour
    ↓ (they ask more questions)
Provide value, share portfolio
    ↓ (they express interest)
Offer free consultation call
    ↓ (they book)
Abdul takes the call
    ↓
Convert to paying client
```

### Templates for common scenarios:

**"How much does an app cost?"**
```
Great question! App costs vary widely based on features and complexity. 
A simple app: $5K-15K. Medium complexity: $15K-50K. Complex: $50K+.

We've built apps at every level — happy to give you a specific 
estimate if you share your idea. DM us anytime!
```

**"Can you build [specific app]?"**
```
Absolutely! We've built similar apps before — check out [relevant 
portfolio piece]. Would love to hear more about your vision.
DM us or email hello@blacklayers.com for a free consultation!
```

**"I love your work!"**
```
Thank you so much! That means a lot to our team. 
Which project caught your eye? We'd love to share the story behind it!
```

---

## Metrics To Track Weekly

| Metric | Target (Month 1) | Target (Month 3) |
|--------|------------------|-------------------|
| Twitter followers | 200 | 1000 |
| LinkedIn connections | 300 | 500 |
| Instagram followers | 150 | 500 |
| Leads found | 10/week | 25/week |
| Hot leads (score 7+) | 2/week | 5/week |
| Replies sent | 50/week | 100/week |
| Blog posts | 2/week | 3/week |
| Client calls booked | 1/week | 3/week |

---

## Quick Start Checklist For BLAI

1. [ ] Create Twitter/X developer account and get API keys
2. [ ] Create LinkedIn developer app and get credentials
3. [ ] Set up Instagram Business account
4. [ ] Create Reddit API app
5. [ ] Build Workflow 1: Auto-Poster in n8n
6. [ ] Build Workflow 2: Lead Hunter in n8n
7. [ ] Build Workflow 3: Comment Monitor in n8n
8. [ ] Build Workflow 5: Analytics Dashboard in n8n
9. [ ] Start daily posting routine
10. [ ] Send first weekly report to Abdul

**Start with Workflow 1 (Auto-Poster) — it's the foundation for everything else.**
