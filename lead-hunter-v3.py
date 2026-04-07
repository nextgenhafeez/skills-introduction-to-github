#!/usr/bin/env python3
"""
BLAI Lead Hunter v3 — Find REAL clients who need iOS/mobile app development.

Key difference from v2: We filter OUT developers/builders and find BUYERS.
- Negative signals: "I built", "Show HN", "my project", "open source"
- Positive signals: "need developer", "looking for", "hire", "budget", "build my app"
- Sources: Reddit (proper auth), HackerNews (Ask HN only), Upwork RSS, Product Hunt
"""

import requests
import json
import os
import re
import time
import random
from datetime import datetime, timedelta
from pathlib import Path

DATE = datetime.now().strftime("%Y-%m-%d")
LEADS_DIR = Path.home() / ".openclaw/memory"
LEADS_FILE = LEADS_DIR / "leads-database.json"
REPORT_FILE = LEADS_DIR / f"lead-report-{DATE}.txt"
LEADS_DIR.mkdir(parents=True, exist_ok=True)

HEADERS = {
    "User-Agent": "BLAI-LeadHunter/3.0 (blacklayers.ca; lead research bot)"
}

# === NEGATIVE SIGNALS — These mean the person is a BUILDER, not a BUYER ===
BUILDER_SIGNALS = [
    "i built", "i made", "i created", "we built", "we made", "we created",
    "my project", "our project", "my app", "i'm building", "we're building",
    "show hn:", "i launched", "we launched", "my startup",
    "open source", "open-source", "oss", "self-hosted",
    "here's my", "check out my", "introducing my", "just shipped",
    "side project", "weekend project", "hobby project",
    "i wrote", "we wrote", "i developed", "we developed",
    "my first", "built with", "made with", "powered by",
    "demo:", "release:", "v1.", "v2.", "beta",
    "i'm the developer", "i'm the founder and developer",
    "here is the source", "github.com/", "gitlab.com/",
]

# === NOT-A-CLIENT SIGNALS — These are companies hiring full-time employees, not freelancers ===
FULLTIME_JOB_SIGNALS = [
    "developer advocate", "developer relations", "devrel",
    "developer success", "developer experience",
    "we are hiring", "we're hiring", "join our team", "join us",
    "full-time", "full time", "part-time position",
    "apply now", "apply here", "send your resume", "send your cv",
    "benefits include", "competitive salary", "equity",
    "our team is growing", "come work at",
    "is hiring a", "is hiring an",
    "senior software engineer", "staff engineer",
    "engineering manager", "tech lead position",
]

# === COMPETITOR SIGNALS — These are developers OFFERING services, not buyers ===
COMPETITOR_SIGNALS = [
    "[for hire]", "[for-hire]", "for hire",
    "available for freelance", "available for work",
    "open for projects", "looking for work",
    "i'm a developer", "i'm a designer",
    "my services", "my rates", "my portfolio",
    "hire me", "/hr", "per hour",
    "years of experience crafting",
    "i can build", "i will build",
]

# === BUYER SIGNALS — These mean the person NEEDS a developer ===
STRONG_BUYER_SIGNALS = {
    # Direct hiring intent (+35 each)
    "looking for.*developer": 35,
    "need.*developer": 35,
    "hiring.*developer": 35,
    "looking for.*programmer": 35,
    "need.*app built": 35,
    "want.*app built": 35,
    "looking to hire": 35,
    "want to build an app": 35,
    "need someone to build": 35,
    "can anyone build": 35,
    "who can build": 35,
    "recommend.*developer": 35,
    "find.*developer": 30,
    "seeking.*developer": 35,
    "contractor.*mobile": 30,
    "freelancer.*app": 30,
    "agency.*app": 30,
    "outsource.*development": 30,
}

TECH_MATCH_SIGNALS = {
    # iOS/Mobile specific (+20 each)
    "ios app": 20,
    "iphone app": 20,
    "ipad app": 20,
    "swift developer": 20,
    "swiftui": 20,
    "app store": 15,
    "mobile app": 15,
    "react native": 12,
    "flutter": 12,
    "android app": 10,
    "cross.?platform": 10,
}

BUDGET_SIGNALS = {
    # Money/budget mentioned (+20 each)
    "budget": 20,
    "\\$\\d": 20,
    "cost.*app": 20,
    "how much.*app": 15,
    "pricing": 15,
    "quote": 15,
    "estimate": 15,
    "invest.*app": 20,
    "funding": 10,
    "pay.*developer": 20,
}

URGENCY_SIGNALS = {
    "asap": 15,
    "urgent": 15,
    "this week": 15,
    "this month": 10,
    "deadline": 15,
    "fast turnaround": 15,
    "immediately": 15,
    "as soon as possible": 15,
}

BUSINESS_CONTEXT = {
    "startup": 8,
    "saas": 8,
    "founder": 8,
    "entrepreneur": 8,
    "small business": 10,
    "my business": 10,
    "company needs": 10,
    "client.*app": 10,
    "mvp": 12,
    "prototype": 10,
    "proof of concept": 10,
    "minimum viable": 12,
}


def load_leads():
    if LEADS_FILE.exists():
        try:
            return json.loads(LEADS_FILE.read_text())
        except Exception:
            pass
    return {"leads": [], "last_scan": None}


def save_leads(data):
    data["last_scan"] = datetime.now().isoformat()
    # Keep only last 90 days of leads
    cutoff = (datetime.now() - timedelta(days=90)).strftime("%Y-%m-%d")
    data["leads"] = [l for l in data["leads"] if l.get("date_found", "") >= cutoff]
    LEADS_FILE.write_text(json.dumps(data, indent=2, default=str))


def is_builder(title, text=""):
    """Return True if this is a developer showing off, NOT a buyer."""
    combined = f"{title} {text}".lower()
    for signal in BUILDER_SIGNALS:
        if signal in combined:
            return True
    return False


def is_fulltime_job(title, text=""):
    """Return True if this is a company hiring employees (not looking for freelancers)."""
    combined = f"{title} {text}".lower()
    matches = 0
    for signal in FULLTIME_JOB_SIGNALS:
        if signal in combined:
            matches += 1
    # Need 2+ signals to be sure it's a job posting (one might be coincidence)
    return matches >= 2


def is_competitor(title, text=""):
    """Return True if this is a developer/designer OFFERING services (competitor, not buyer)."""
    combined = f"{title} {text}".lower()
    for signal in COMPETITOR_SIGNALS:
        if signal in combined:
            return True
    return False


def has_mobile_context(title, text=""):
    """Check if the lead has ANY relation to mobile/app development."""
    combined = f"{title} {text}".lower()
    mobile_words = [
        "app", "mobile", "ios", "android", "iphone", "ipad",
        "swift", "swiftui", "react native", "flutter",
        "app store", "play store", "mobile app",
        "cross platform", "native app",
    ]
    return any(word in combined for word in mobile_words)


def score_lead(title, text=""):
    """Score a lead based on buyer intent. Returns 0-100.

    IMPORTANT: A lead must have EITHER mobile/app context OR strong buyer signals
    with budget to score above COLD. Generic "hiring developer" without app context
    scores low.
    """
    combined = f"{title} {text}".lower()
    score = 0

    # Skip full-time job postings and competitors offering services
    if is_fulltime_job(title, text):
        return 0
    if is_competitor(title, text):
        return 0

    # Check all signal categories
    buyer_score = 0
    for pattern, points in STRONG_BUYER_SIGNALS.items():
        if re.search(pattern, combined):
            buyer_score += points

    tech_score = 0
    for pattern, points in TECH_MATCH_SIGNALS.items():
        if re.search(pattern, combined):
            tech_score += points

    budget_score = 0
    for pattern, points in BUDGET_SIGNALS.items():
        if re.search(pattern, combined):
            budget_score += points

    urgency_score = 0
    for pattern, points in URGENCY_SIGNALS.items():
        if re.search(pattern, combined):
            urgency_score += points

    biz_score = 0
    for pattern, points in BUSINESS_CONTEXT.items():
        if re.search(pattern, combined):
            biz_score += points

    # CRITICAL: If no mobile/app context AND no tech match, cap score at 25 (COLD)
    # This prevents generic "hiring developer" posts from scoring HOT
    if tech_score == 0 and not has_mobile_context(title, text):
        return min(buyer_score + biz_score, 25)

    score = buyer_score + tech_score + budget_score + urgency_score + biz_score
    return min(score, 100)


def get_tier(score):
    if score >= 60:
        return "HOT"
    if score >= 30:
        return "WARM"
    return "COLD"


# =============================================================================
# SOURCE 1: Reddit — The #1 source for real client leads
# =============================================================================
def get_reddit_token():
    """Get Reddit OAuth token using script app credentials.
    Set REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET env vars.
    Create app at https://www.reddit.com/prefs/apps (choose 'script' type).
    """
    client_id = os.environ.get("REDDIT_CLIENT_ID", "")
    client_secret = os.environ.get("REDDIT_CLIENT_SECRET", "")

    if not client_id or not client_secret:
        print("    Reddit: No API credentials. Set REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET.")
        print("    Create app at: https://www.reddit.com/prefs/apps (type: script)")
        return None

    try:
        r = requests.post(
            "https://www.reddit.com/api/v1/access_token",
            auth=(client_id, client_secret),
            data={"grant_type": "client_credentials"},
            headers={"User-Agent": "BLAI-LeadHunter/3.0 (by /u/blacklayersai)"},
            timeout=10
        )
        if r.status_code == 200:
            return r.json().get("access_token")
        else:
            print(f"    Reddit auth failed: {r.status_code}")
    except Exception as e:
        print(f"    Reddit auth error: {e}")
    return None


def search_reddit():
    """Search Reddit for people actively looking to hire developers."""
    leads = []

    token = get_reddit_token()
    if not token:
        # Fallback: try without auth (may get blocked)
        return search_reddit_noauth()

    headers = {
        "Authorization": f"Bearer {token}",
        "User-Agent": "BLAI-LeadHunter/3.0 (by /u/blacklayersai)"
    }

    # Subreddits where BUYERS post (not where devs hang out)
    subreddits_and_queries = [
        ("forhire", ["[Hiring] iOS", "[Hiring] mobile", "[Hiring] app"]),
        ("startups", ["need developer", "looking for developer", "need app built"]),
        ("entrepreneur", ["build my app", "need mobile app", "looking for developer"]),
        ("smallbusiness", ["need app", "mobile app for business"]),
        ("cofounder", ["looking for technical", "non-technical founder"]),
        ("iOSProgramming", ["[Hiring]", "looking for freelance"]),
        ("slavelabour", ["app", "ios", "mobile app", "build me"]),
    ]

    for sub, queries in subreddits_and_queries:
        for q in queries:
            try:
                url = f"https://oauth.reddit.com/r/{sub}/search"
                params = {
                    "q": q,
                    "sort": "new",
                    "t": "week",
                    "limit": 10,
                    "restrict_sr": "true"
                }
                r = requests.get(url, headers=headers, params=params, timeout=15)

                if r.status_code == 200:
                    data = r.json()
                    children = data.get("data", {}).get("children", [])
                    for post in children:
                        p = post.get("data", {})
                        title = p.get("title", "")
                        text = p.get("selftext", "")

                        if is_builder(title, text):
                            continue

                        score = score_lead(title, text)
                        if score >= 20:
                            leads.append({
                                "source": "reddit",
                                "subreddit": sub,
                                "title": title[:200],
                                "author": p.get("author", "unknown"),
                                "url": f"https://reddit.com{p.get('permalink', '')}",
                                "score": score,
                                "tier": get_tier(score),
                                "date_found": DATE,
                                "preview": text[:300],
                                "upvotes": p.get("ups", 0),
                                "comments": p.get("num_comments", 0),
                                "status": "new",
                                "outreach_sent": False,
                                "follow_up_date": None
                            })

                elif r.status_code == 429:
                    print(f"    Reddit rate-limited on r/{sub}, waiting 60s...")
                    time.sleep(60)

                time.sleep(1)  # Be nice to Reddit
            except Exception as e:
                print(f"    Error on r/{sub}: {e}")
                continue

    return leads


def search_reddit_noauth():
    """Search Reddit via RSS feeds — no API key needed, no rate limits."""
    leads = []
    print("    Using Reddit RSS feeds (no auth needed)...")

    # RSS feeds for subreddits — these work without API access
    feeds = [
        ("forhire", "https://www.reddit.com/r/forhire/search.rss?q=%5BHiring%5D+iOS+OR+%5BHiring%5D+mobile+OR+%5BHiring%5D+app&sort=new&t=week&restrict_sr=on"),
        ("forhire_new", "https://www.reddit.com/r/forhire/new/.rss?limit=25"),
        ("startups", "https://www.reddit.com/r/startups/search.rss?q=need+developer+OR+looking+for+developer+OR+need+app&sort=new&t=week&restrict_sr=on"),
        ("entrepreneur", "https://www.reddit.com/r/entrepreneur/search.rss?q=build+my+app+OR+need+developer+OR+mobile+app&sort=new&t=week&restrict_sr=on"),
        ("smallbusiness", "https://www.reddit.com/r/smallbusiness/search.rss?q=need+app+OR+mobile+app+OR+looking+for+developer&sort=new&t=week&restrict_sr=on"),
        ("cofounder", "https://www.reddit.com/r/cofounder/new/.rss?limit=15"),
    ]

    for sub_name, feed_url in feeds:
        try:
            r = requests.get(feed_url, headers={
                "User-Agent": "Mozilla/5.0 (compatible; BLAI/3.0)"
            }, timeout=15)

            if r.status_code == 200 and "<entry>" in r.text:
                # Parse Atom XML manually (no external deps needed)
                import re as regex
                entries = r.text.split("<entry>")[1:]  # Skip the feed header
                for entry in entries[:10]:
                    # Extract title
                    title_match = regex.search(r"<title[^>]*>(.*?)</title>", entry, regex.DOTALL)
                    title = title_match.group(1).strip() if title_match else ""
                    # Clean HTML entities
                    title = title.replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">").replace("&#39;", "'").replace("&quot;", '"')

                    # Extract link
                    link_match = regex.search(r'<link[^>]*href="([^"]*)"', entry)
                    url = link_match.group(1).strip() if link_match else ""

                    # Extract content/summary
                    content_match = regex.search(r"<content[^>]*>(.*?)</content>", entry, regex.DOTALL)
                    content = content_match.group(1).strip() if content_match else ""
                    # Strip HTML tags for scoring
                    content_text = regex.sub(r"<[^>]+>", " ", content)
                    content_text = content_text.replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")

                    # Extract author
                    author_match = regex.search(r"<name>(.*?)</name>", entry)
                    author = author_match.group(1).strip() if author_match else "unknown"
                    author = author.replace("/u/", "")

                    if not title or not url:
                        continue

                    if is_builder(title, content_text):
                        continue

                    if is_fulltime_job(title, content_text):
                        continue

                    score = score_lead(title, content_text)
                    if score >= 20:
                        leads.append({
                            "source": "reddit",
                            "subreddit": sub_name,
                            "title": title[:200],
                            "author": author,
                            "url": url,
                            "score": score,
                            "tier": get_tier(score),
                            "date_found": DATE,
                            "preview": content_text[:300],
                            "status": "new",
                            "outreach_sent": False,
                            "follow_up_date": None
                        })

            elif r.status_code == 403:
                print(f"    r/{sub_name}: RSS also blocked (403)")
            else:
                print(f"    r/{sub_name}: {r.status_code}, no entries found")

            time.sleep(1)
        except Exception as e:
            print(f"    r/{sub_name} error: {e}")
            continue

    return leads


# =============================================================================
# SOURCE 2: HackerNews — Only "Ask HN" posts (buyers asking for help)
# =============================================================================
def search_hackernews():
    """Search HN for Ask HN posts where people need developers. Skip Show HN."""
    leads = []

    # ONLY queries that indicate BUYING intent
    queries = [
        "looking for developer",
        "need app developer",
        "hire iOS developer",
        "need mobile developer",
        "build my app",
        "non-technical founder",
        "how to find developer",
        "cost to build app",
        "need technical cofounder",
        "looking for freelance developer",
        "recommend app developer",
    ]

    for query in queries:
        try:
            url = "https://hn.algolia.com/api/v1/search_by_date"
            params = {
                "query": query,
                "tags": "ask_hn",  # ONLY Ask HN — these are people asking for help
                "numericFilters": f"created_at_i>{int((datetime.now() - timedelta(days=14)).timestamp())}",
                "hitsPerPage": 10
            }
            r = requests.get(url, params=params, headers=HEADERS, timeout=10)
            if r.status_code == 200:
                for hit in r.json().get("hits", []):
                    title = hit.get("title", "")
                    text = hit.get("story_text", "") or ""

                    # CRITICAL: Skip builders showing off
                    if is_builder(title, text):
                        continue

                    # Skip "Show HN" that leaked through
                    if title.lower().startswith("show hn"):
                        continue

                    score = score_lead(title, text)
                    if score >= 20:
                        leads.append({
                            "source": "hackernews",
                            "title": title[:200],
                            "author": hit.get("author", "unknown"),
                            "url": f"https://news.ycombinator.com/item?id={hit.get('objectID', '')}",
                            "score": score,
                            "tier": get_tier(score),
                            "date_found": DATE,
                            "preview": text[:300],
                            "comments": hit.get("num_comments", 0),
                            "points": hit.get("points", 0),
                            "status": "new",
                            "outreach_sent": False,
                            "follow_up_date": None
                        })
            time.sleep(0.5)
        except Exception:
            continue

    return leads


# =============================================================================
# SOURCE 3: Product Hunt — Find startups WITHOUT mobile apps
# =============================================================================
def search_producthunt():
    """Find recent Product Hunt launches that are web-only (no mobile app)."""
    leads = []

    dev_token = os.environ.get("PRODUCTHUNT_DEV_TOKEN", "")

    if not dev_token:
        print("    Product Hunt: No dev token. Set PRODUCTHUNT_DEV_TOKEN env var.")
        return leads

    try:
        access_token = dev_token

        # GraphQL query for today's posts
        query = """
        {
          posts(order: NEWEST, first: 20) {
            edges {
              node {
                name
                tagline
                url
                website
                votesCount
                makers {
                  name
                  username
                }
                topics {
                  edges {
                    node {
                      name
                    }
                  }
                }
              }
            }
          }
        }
        """

        r = requests.post(
            "https://api.producthunt.com/v2/api/graphql",
            json={"query": query},
            headers={
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            },
            timeout=15
        )

        if r.status_code == 200:
            data = r.json()
            edges = data.get("data", {}).get("posts", {}).get("edges", [])
            for edge in edges:
                node = edge.get("node", {})
                name = node.get("name", "")
                tagline = node.get("tagline", "")
                topics = [t["node"]["name"] for t in node.get("topics", {}).get("edges", [])]
                topics_str = ", ".join(topics)

                # Check if they DON'T have mobile topics (web-only = opportunity)
                has_mobile = any(t.lower() in ["ios", "android", "mobile", "iphone"] for t in topics)

                if not has_mobile:
                    score = score_lead(name, tagline)
                    score += 15  # Bonus: confirmed no mobile app
                    maker_name = "unknown"
                    makers = node.get("makers", [])
                    if makers:
                        maker_name = makers[0].get("name", makers[0].get("username", "unknown"))

                    leads.append({
                        "source": "producthunt",
                        "title": f"{name} — {tagline}"[:200],
                        "author": maker_name,
                        "url": node.get("url", ""),
                        "website": node.get("website", ""),
                        "score": min(score, 100),
                        "tier": get_tier(min(score, 100)),
                        "date_found": DATE,
                        "preview": f"Web product without mobile app. Topics: {topics_str}. Tagline: {tagline}",
                        "votes": node.get("votesCount", 0),
                        "status": "new",
                        "outreach_type": "cold_email",
                        "outreach_sent": False,
                        "follow_up_date": None
                    })
        else:
            print(f"    Product Hunt API error: {r.status_code}")

    except Exception as e:
        print(f"    Product Hunt error: {e}")

    return leads


# =============================================================================
# SOURCE 4: Dev.to — People asking for developer help
# =============================================================================
def search_devto():
    """Search Dev.to for posts where people need developers."""
    leads = []
    try:
        # Search for hiring/help-wanted posts
        for tag in ["hiring", "helpwanted", "collaboration"]:
            url = "https://dev.to/api/articles"
            params = {"tag": tag, "per_page": 15, "state": "fresh"}
            r = requests.get(url, headers=HEADERS, params=params, timeout=10)

            if r.status_code == 200:
                for article in r.json():
                    title = article.get("title", "")
                    desc = article.get("description", "")

                    if is_builder(title, desc):
                        continue

                    score = score_lead(title, desc)
                    if score >= 20:
                        leads.append({
                            "source": "devto",
                            "title": title[:200],
                            "author": article.get("user", {}).get("username", "unknown"),
                            "url": article.get("url", ""),
                            "score": score,
                            "tier": get_tier(score),
                            "date_found": DATE,
                            "preview": desc[:300],
                            "reactions": article.get("positive_reactions_count", 0),
                            "status": "new",
                            "outreach_sent": False,
                            "follow_up_date": None
                        })
            time.sleep(0.5)
    except Exception as e:
        print(f"    Dev.to error: {e}")

    return leads


# =============================================================================
# SOURCE 5: Twitter/X — Search for hiring tweets (via Nitter)
# =============================================================================
def search_twitter():
    """Search for tweets where people need app developers."""
    leads = []
    # Note: Direct Twitter API requires auth. Using search via public instances.
    queries = [
        "looking for iOS developer",
        "need app developer",
        "hiring mobile developer",
        "need someone to build my app",
        "looking for app developer",
    ]

    for query in queries:
        try:
            # Try searching via Twitter's public search
            url = f"https://syndication.twitter.com/srv/timeline-profile/screen-name/search"
            params = {"q": query, "f": "live"}
            r = requests.get(
                f"https://api.twitter.com/2/tweets/search/recent",
                params={"query": f"{query} -is:retweet lang:en", "max_results": 10},
                headers=HEADERS,
                timeout=10
            )
            # Twitter API requires Bearer token — log this as a TODO
            if r.status_code == 401 or r.status_code == 403:
                print("    Twitter: needs API auth (Bearer token). Skipping.")
                break
        except Exception:
            continue

    return leads


# =============================================================================
# DEDUPLICATION & REPORTING
# =============================================================================
def deduplicate(leads, existing):
    """Remove duplicates by URL."""
    existing_urls = {l.get("url") for l in existing}
    seen = set()
    unique = []
    for lead in leads:
        url = lead.get("url", "")
        if url and url not in existing_urls and url not in seen:
            seen.add(url)
            unique.append(lead)
    return unique


def generate_reply(lead):
    """Generate a personalized, ready-to-paste reply for a lead."""
    source = lead.get("source", "")
    title = lead.get("title", "")
    author = lead.get("author", "")
    preview = lead.get("preview", "")

    # Clean HTML from preview
    import re as rx
    preview_clean = rx.sub(r"<[^>]+>", "", preview)
    preview_clean = preview_clean.replace("&amp;", "&").replace("&quot;", '"').replace("&#39;", "'").replace("&lt;", "<").replace("&gt;", ">").strip()

    if source == "reddit":
        # Detect what they need from title/preview
        needs_website = any(w in title.lower() + preview_clean.lower() for w in ["website", "web site", "landing page"])
        needs_app = any(w in title.lower() + preview_clean.lower() for w in ["app", "mobile", "ios", "android"])
        needs_dev = any(w in title.lower() + preview_clean.lower() for w in ["developer", "programmer", "coder", "build"])

        if needs_app:
            return (
                f"Hey! Saw your post about needing app development.\n"
                f"\n"
                f"I run Black Layers — we've shipped 20+ iOS apps including one that makes $10K+/month. "
                f"We handle everything from design to App Store submission.\n"
                f"\n"
                f"Happy to chat about your project — no commitment. "
                f"You can check our work at blacklayers.ca\n"
                f"\n"
                f"Feel free to DM or reach me on WhatsApp: +212641503230"
            )
        elif needs_website:
            return (
                f"Hey! I saw your post — I totally understand the frustration.\n"
                f"\n"
                f"I run Black Layers, we build websites and apps for small businesses. "
                f"We've shipped 20+ projects with zero rejections. "
                f"We could probably help you out at a fair price.\n"
                f"\n"
                f"Check our portfolio: blacklayers.ca\n"
                f"Happy to chat — DM me or WhatsApp: +212641503230"
            )
        else:
            return (
                f"Hey! Saw your post and thought I could help.\n"
                f"\n"
                f"I'm Abdul from Black Layers — we build iOS apps and websites for startups and small businesses. "
                f"20+ apps shipped, including AdClose ($10K+/month revenue).\n"
                f"\n"
                f"Would love to learn more about your project.\n"
                f"Portfolio: blacklayers.ca | WhatsApp: +212641503230"
            )

    elif source == "hackernews":
        return (
            f"I run a small iOS dev studio (Black Layers) — we've shipped 20+ apps. "
            f"If you're looking for development help, happy to chat.\n"
            f"\n"
            f"Portfolio: blacklayers.ca"
        )

    elif source == "producthunt":
        product_name = title.split(" — ")[0] if " — " in title else title[:30]
        return (
            f"Subject: {product_name} would be amazing as a mobile app\n"
            f"\n"
            f"Hi {author},\n"
            f"\n"
            f"Congrats on the Product Hunt launch! {product_name} looks great.\n"
            f"\n"
            f"I noticed you don't have a mobile app yet. We specialize in turning web products "
            f"into iOS apps at Black Layers. We've shipped 20+ apps, including one generating $10K+/month.\n"
            f"\n"
            f"Would a mobile version make sense? Quick 15-min call, no strings attached.\n"
            f"\n"
            f"Abdul Hafeez\n"
            f"Black Layers | blacklayers.ca\n"
            f"WhatsApp: +1 (587) 429-6200\n"
            f"Email: info@blacklayers.ca"
        )

    elif source == "devto":
        return (
            f"Hey {author}! Saw your post.\n"
            f"\n"
            f"I'm Abdul from Black Layers — we build iOS apps and web projects. "
            f"20+ apps shipped. Would love to help if you need development support.\n"
            f"\n"
            f"blacklayers.ca | WhatsApp: +1 (587) 429-6200\n"
            f"Email: info@blacklayers.ca"
        )

    return ""


def generate_report(new_leads, total_db, source_counts):
    """Generate WhatsApp-friendly report matching skill format."""
    hot = [l for l in new_leads if l["tier"] == "HOT"]
    warm = [l for l in new_leads if l["tier"] == "WARM"]
    cold = [l for l in new_leads if l["tier"] == "COLD"]

    lines = []
    lines.append(f"🎯 LEAD REPORT — {DATE}")
    lines.append("")

    # Hot leads with full detail + ready-to-paste reply
    if hot:
        lines.append(f"🔥 HOT LEADS ({len(hot)}):")
        for i, l in enumerate(hot[:10], 1):
            lines.append(f"{i}. [{l['source'].upper()}] {l['title'][:80]}")
            lines.append(f"   Score: {l['score']}/100 | By: {l['author']}")
            lines.append(f"   {l['url']}")
            if l.get("preview"):
                lines.append(f"   Preview: {l['preview'][:120]}...")
            # Generate ready-to-paste reply
            reply = generate_reply(l)
            if reply:
                lines.append(f"")
                lines.append(f"   ✏️ COPY-PASTE REPLY:")
                lines.append(f"   ---")
                for reply_line in reply.split("\n"):
                    lines.append(f"   {reply_line}")
                lines.append(f"   ---")
            lines.append("")
    else:
        lines.append("🔥 HOT LEADS: 0")
        lines.append("")

    # Warm leads with reply for top 3
    if warm:
        lines.append(f"🟡 WARM LEADS ({len(warm)}):")
        for i, l in enumerate(warm[:5], 1):
            lines.append(f"{i}. [{l['source'].upper()}] {l['title'][:80]}")
            lines.append(f"   Score: {l['score']}/100 | {l['url']}")
            if i <= 3:
                reply = generate_reply(l)
                if reply:
                    lines.append(f"   ✏️ REPLY: {reply.split(chr(10))[0][:100]}...")
        lines.append("")
    else:
        lines.append("🟡 WARM LEADS: 0")
        lines.append("")

    lines.append(f"🔵 COLD LEADS: {len(cold)}")
    lines.append("")

    # Source breakdown
    lines.append("SOURCES SEARCHED:")
    for source, count in source_counts.items():
        status = f"{count} leads" if count > 0 else "0 (check auth/rate limits)"
        lines.append(f"  • {source}: {status}")
    lines.append("")

    # Actions needed
    lines.append("⚡ ACTIONS NEEDED:")
    if hot:
        for l in hot[:3]:
            lines.append(f"  • REACH OUT to {l['author']} ({l['source']}) — {l['title'][:50]}")
    if not hot and not warm:
        lines.append("  • No strong leads today. Review search queries.")
    lines.append("")

    # Follow-ups due
    lines.append("FOLLOW-UPS DUE:")
    lines.append("  • (checked from database — see below)")
    lines.append("")

    lines.append("SUMMARY:")
    lines.append(f"  • New leads today: {len(new_leads)}")
    lines.append(f"  • Hot: {len(hot)} | Warm: {len(warm)} | Cold: {len(cold)}")
    lines.append(f"  • Total in database: {total_db}")
    lines.append(f"  • Builders filtered out: (auto-removed by v3 filters)")

    return "\n".join(lines)


def check_followups(db):
    """Check for leads that need follow-up today."""
    today = DATE
    due = []
    for lead in db.get("leads", []):
        if (lead.get("follow_up_date") == today and
            lead.get("status") in ("awaiting_response", "outreach_sent") and
            lead.get("outreach_sent")):
            due.append(lead)
    if due:
        print(f"\n⚠️  FOLLOW-UPS DUE TODAY: {len(due)}")
        for l in due:
            print(f"  → {l['author']} ({l['source']}) — {l['title'][:60]}")
    return due


def main():
    print(f"BLAI Lead Hunter v3 — {DATE}")
    print("=" * 50)
    print("Mode: BUYER-FOCUSED (builders filtered out)")
    print()

    db = load_leads()
    existing = db.get("leads", [])

    source_counts = {}

    # 1. Reddit — Primary source
    print("[1/5] Searching Reddit (8 subreddits, buyer queries)...")
    reddit = search_reddit()
    reddit = [l for l in reddit if not is_builder(l.get("title", ""), l.get("preview", ""))]
    source_counts["Reddit"] = len(reddit)
    print(f"  → {len(reddit)} buyer leads (builders filtered)")

    # 2. HackerNews — Ask HN only
    print("[2/5] Searching HackerNews (Ask HN only, 11 queries)...")
    hn = search_hackernews()
    source_counts["HackerNews"] = len(hn)
    print(f"  → {len(hn)} leads (Show HN excluded)")

    # 3. Product Hunt — Startups without mobile apps
    print("[3/5] Searching Product Hunt (web-only startups)...")
    ph = search_producthunt()
    source_counts["ProductHunt"] = len(ph)
    print(f"  → {len(ph)} web-only startups (potential mobile app clients)")

    # 4. Dev.to
    print("[4/5] Searching Dev.to (hiring/collab tags)...")
    devto = search_devto()
    devto = [l for l in devto if not is_builder(l.get("title", ""), l.get("preview", ""))]
    source_counts["Dev.to"] = len(devto)
    print(f"  → {len(devto)} leads")

    # 5. Twitter (needs auth)
    print("[5/5] Searching Twitter/X...")
    twitter = search_twitter()
    source_counts["Twitter"] = len(twitter)
    print(f"  → {len(twitter)} leads")

    # Combine and deduplicate
    all_leads = reddit + hn + ph + devto + twitter
    new_leads = deduplicate(all_leads, existing)
    new_leads.sort(key=lambda x: x["score"], reverse=True)

    print(f"\nTotal raw: {len(all_leads)} | New unique: {len(new_leads)}")

    # Check follow-ups
    check_followups(db)

    # Save to database
    db["leads"] = existing + new_leads
    save_leads(db)

    # Generate report
    report = generate_report(new_leads, len(db["leads"]), source_counts)
    print("\n" + report)
    REPORT_FILE.write_text(report)

    # Quality check
    hot = [l for l in new_leads if l["tier"] == "HOT"]
    if not hot:
        print("\n⚠️  NO HOT LEADS TODAY.")
        print("   This is normal — real buyer leads are rare.")
        print("   Quality > quantity. One real client > 100 HN posts.")

    return report


if __name__ == "__main__":
    main()
