#!/usr/bin/env python3
"""
Lead Hunter — Find people who NEED to hire iOS/mobile developers.
Searches Reddit, HackerNews, ProductHunt. Scores and reports leads.
"""

import json
import time
import requests
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.brain import think_simple
from pathlib import Path

MEMORY_DIR = Path(__file__).parent.parent / "memory"
LEADS_FILE = MEMORY_DIR / "leads.json"

# Negative signals — skip these (builders, not buyers)
SKIP_PATTERNS = [
    "i built", "i made", "i created", "we built", "show hn",
    "my project", "side project", "open source", "i launched",
    "just shipped", "built with", "made with", "check out my"
]

# Positive signals — these are buyers
BUY_SIGNALS = [
    "need developer", "looking for developer", "hiring developer",
    "need app built", "want app built", "looking to hire",
    "need ios", "need mobile app", "cost to build",
    "recommend developer", "need technical cofounder"
]


def search_reddit(subreddit: str, keywords: list, limit: int = 10) -> list:
    """Search a subreddit for potential leads."""
    leads = []
    headers = {"User-Agent": "BLAI-LeadHunter/1.0"}

    for kw in keywords:
        try:
            url = f"https://www.reddit.com/r/{subreddit}/search.json"
            resp = requests.get(url, params={
                "q": kw, "sort": "new", "t": "week", "limit": limit
            }, headers=headers, timeout=15)

            if resp.status_code != 200:
                continue

            data = resp.json()
            for post in data.get("data", {}).get("children", []):
                p = post["data"]
                title = p.get("title", "").lower()
                text = p.get("selftext", "").lower()
                combined = f"{title} {text}"

                # Skip builders
                if any(skip in combined for skip in SKIP_PATTERNS):
                    continue

                # Score lead
                score = 0
                for signal in BUY_SIGNALS:
                    if signal in combined:
                        score += 25

                if any(w in combined for w in ["ios", "iphone", "swift"]):
                    score += 20
                if any(w in combined for w in ["mobile app", "react native"]):
                    score += 15
                if any(w in combined for w in ["budget", "cost", "quote", "$"]):
                    score += 20
                if any(w in combined for w in ["asap", "urgent", "deadline"]):
                    score += 15

                if score > 0:
                    leads.append({
                        "source": f"reddit/r/{subreddit}",
                        "title": p.get("title", ""),
                        "author": p.get("author", ""),
                        "url": f"https://reddit.com{p.get('permalink', '')}",
                        "score": min(score, 100),
                        "preview": p.get("selftext", "")[:200],
                        "date_found": time.strftime("%Y-%m-%d"),
                        "status": "new",
                        "outreach_sent": False
                    })
        except Exception as e:
            continue

    return leads


def search_hackernews(limit: int = 10) -> list:
    """Search HN for Ask HN posts about needing developers."""
    leads = []
    keywords = [
        "hire developer", "need app developer", "looking for developer",
        "cost to build app", "need technical cofounder", "need ios developer"
    ]

    for kw in keywords:
        try:
            url = "https://hn.algolia.com/api/v1/search"
            resp = requests.get(url, params={
                "query": kw, "tags": "ask_hn", "numericFilters": "created_at_i>" + str(int(time.time()) - 604800)
            }, timeout=15)

            if resp.status_code != 200:
                continue

            for hit in resp.json().get("hits", [])[:limit]:
                title = hit.get("title", "").lower()
                if any(skip in title for skip in SKIP_PATTERNS):
                    continue

                score = 0
                for signal in BUY_SIGNALS:
                    if signal in title:
                        score += 30
                if "ios" in title or "mobile" in title:
                    score += 20

                if score > 0:
                    leads.append({
                        "source": "hackernews",
                        "title": hit.get("title", ""),
                        "author": hit.get("author", ""),
                        "url": f"https://news.ycombinator.com/item?id={hit.get('objectID', '')}",
                        "score": min(score, 100),
                        "preview": hit.get("title", ""),
                        "date_found": time.strftime("%Y-%m-%d"),
                        "status": "new",
                        "outreach_sent": False
                    })
        except:
            continue

    return leads


def deduplicate(leads: list, existing: list) -> list:
    """Remove leads already in database."""
    existing_urls = {l["url"] for l in existing}
    return [l for l in leads if l["url"] not in existing_urls]


def run_hunt() -> dict:
    """Run a full lead hunting session."""
    MEMORY_DIR.mkdir(parents=True, exist_ok=True)

    # Load existing leads
    existing = []
    if LEADS_FILE.exists():
        existing = json.loads(LEADS_FILE.read_text()).get("leads", [])

    # Search all sources
    all_leads = []

    subreddits = ["forhire", "startups", "entrepreneur", "smallbusiness", "cofounder", "iOSProgramming"]
    search_terms = ["need ios developer", "hire app developer", "need mobile app", "looking for developer"]

    for sub in subreddits:
        all_leads.extend(search_reddit(sub, search_terms))

    all_leads.extend(search_hackernews())

    # Deduplicate
    new_leads = deduplicate(all_leads, existing)

    # Sort by score
    new_leads.sort(key=lambda x: x["score"], reverse=True)

    # Save
    existing.extend(new_leads)
    LEADS_FILE.write_text(json.dumps({"leads": existing, "last_scan": time.strftime("%Y-%m-%dT%H:%M:%S")}, indent=2))

    # Categorize
    hot = [l for l in new_leads if l["score"] >= 60]
    warm = [l for l in new_leads if 30 <= l["score"] < 60]
    cold = [l for l in new_leads if l["score"] < 30]

    return {
        "total_new": len(new_leads),
        "hot": hot,
        "warm": warm,
        "cold": cold,
        "total_in_db": len(existing)
    }


def generate_report(results: dict) -> str:
    """Generate WhatsApp-ready lead report."""
    if results["total_new"] == 0:
        return "Lead scan done. No new leads found today."

    lines = [f"LEAD REPORT — {time.strftime('%b %d')}"]
    lines.append(f"New: {results['total_new']} | Hot: {len(results['hot'])} | Warm: {len(results['warm'])}")

    for lead in results["hot"][:3]:
        lines.append(f"\nHOT ({lead['score']}/100): {lead['title'][:80]}")
        lines.append(f"  {lead['url']}")

    if results["hot"]:
        lines.append(f"\nAction: reach out to {len(results['hot'])} hot leads")

    return "\n".join(lines)


if __name__ == "__main__":
    results = run_hunt()
    print(generate_report(results))
