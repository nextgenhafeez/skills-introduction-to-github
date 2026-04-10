#!/usr/bin/env python3
"""
Lead Hunter Real — Uses Make.com webhooks + direct API searches to find leads.
Combines Reddit/HN search with Make.com webhook triggers for extended reach.
"""

import json
import time
import requests
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.brain import think_simple
from skills.make_com import call_webhook_by_name, create_webhook, _load_webhooks, _get_webhooks_config
from pathlib import Path

MEMORY_DIR = Path(__file__).parent.parent / "memory"
LEADS_FILE = MEMORY_DIR / "leads_real.json"

# Signals for scoring
SKIP_PATTERNS = [
    "i built", "i made", "i created", "we built", "show hn",
    "my project", "side project", "open source", "i launched",
    "just shipped", "built with", "made with", "check out my"
]

BUY_SIGNALS = [
    "need developer", "looking for developer", "hiring developer",
    "need app built", "want app built", "looking to hire",
    "need ios", "need mobile app", "cost to build",
    "recommend developer", "need technical cofounder",
    "freelance developer", "contract developer"
]


def _load_leads() -> list:
    """Load existing leads database."""
    if LEADS_FILE.exists():
        data = json.loads(LEADS_FILE.read_text())
        return data.get("leads", [])
    return []


def _save_leads(leads: list):
    """Save leads database."""
    MEMORY_DIR.mkdir(parents=True, exist_ok=True)
    LEADS_FILE.write_text(json.dumps({
        "leads": leads,
        "last_updated": time.strftime("%Y-%m-%dT%H:%M:%S")
    }, indent=2))


def _score_lead(title: str, text: str) -> int:
    """Score a lead 0-100 based on buy signals."""
    combined = f"{title} {text}".lower()

    if any(skip in combined for skip in SKIP_PATTERNS):
        return 0

    score = 0
    for signal in BUY_SIGNALS:
        if signal in combined:
            score += 25

    if any(w in combined for w in ["ios", "iphone", "swift"]):
        score += 20
    if any(w in combined for w in ["mobile app", "react native", "flutter"]):
        score += 15
    if any(w in combined for w in ["budget", "cost", "quote", "$", "pay"]):
        score += 20
    if any(w in combined for w in ["asap", "urgent", "deadline", "this week"]):
        score += 15

    return min(score, 100)


def search_reddit(query: str, subreddits: list = None, limit: int = 10) -> list:
    """Search Reddit for leads matching query."""
    leads = []
    headers = {"User-Agent": "BLAI-LeadHunter/2.0"}

    if not subreddits:
        subreddits = ["forhire", "startups", "entrepreneur", "smallbusiness",
                       "cofounder", "iOSProgramming", "freelance", "androiddev"]

    for sub in subreddits:
        try:
            resp = requests.get(
                f"https://www.reddit.com/r/{sub}/search.json",
                params={"q": query, "sort": "new", "t": "week", "limit": limit},
                headers=headers,
                timeout=15
            )
            if resp.status_code != 200:
                continue

            for post in resp.json().get("data", {}).get("children", []):
                p = post["data"]
                title = p.get("title", "")
                text = p.get("selftext", "")
                score = _score_lead(title, text)

                if score > 0:
                    leads.append({
                        "source": f"reddit/r/{sub}",
                        "title": title,
                        "author": p.get("author", ""),
                        "url": f"https://reddit.com{p.get('permalink', '')}",
                        "score": score,
                        "preview": text[:200],
                        "date_found": time.strftime("%Y-%m-%d"),
                        "status": "new",
                        "outreach_sent": False
                    })
        except Exception:
            continue

    return leads


def search_hackernews(query: str = None, limit: int = 10) -> list:
    """Search HackerNews for leads."""
    leads = []
    queries = [query] if query else [
        "hire developer", "need app developer", "looking for developer",
        "cost to build app", "need ios developer"
    ]

    for q in queries:
        try:
            resp = requests.get(
                "https://hn.algolia.com/api/v1/search",
                params={
                    "query": q,
                    "tags": "ask_hn",
                    "numericFilters": f"created_at_i>{int(time.time()) - 604800}"
                },
                timeout=15
            )
            if resp.status_code != 200:
                continue

            for hit in resp.json().get("hits", [])[:limit]:
                title = hit.get("title", "")
                score = _score_lead(title, "")

                if score > 0:
                    leads.append({
                        "source": "hackernews",
                        "title": title,
                        "author": hit.get("author", ""),
                        "url": f"https://news.ycombinator.com/item?id={hit.get('objectID', '')}",
                        "score": score,
                        "preview": title,
                        "date_found": time.strftime("%Y-%m-%d"),
                        "status": "new",
                        "outreach_sent": False
                    })
        except Exception:
            continue

    return leads


def send_to_make_webhook(leads: list) -> str:
    """Send leads to Make.com webhook for further processing (if configured)."""
    webhooks = _get_webhooks_config()
    saved = _load_webhooks()

    # Look for a lead-hunting webhook
    webhook_name = None
    for name in list(saved.keys()) + list(webhooks.keys()):
        if "lead" in name.lower():
            webhook_name = name
            break

    if not webhook_name:
        return "No lead-hunting webhook configured in Make.com. Leads saved locally only."

    result = call_webhook_by_name(webhook_name, {
        "leads": leads[:5],  # Send top 5 to avoid overload
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "source": "BLAI lead hunter"
    })
    return result


def hunt_leads(query: str = None, platforms: list = None) -> str:
    """
    Main function — hunt for leads across platforms.
    Returns a WhatsApp-friendly summary.

    Args:
        query: Search query (default: iOS/mobile dev related)
        platforms: List of platforms to search (default: all)
    """
    if not query:
        query = "need ios developer"

    if not platforms:
        platforms = ["reddit", "hackernews"]

    existing = _load_leads()
    existing_urls = {l["url"] for l in existing}

    all_leads = []

    if "reddit" in platforms:
        reddit_leads = search_reddit(query)
        all_leads.extend(reddit_leads)

    if "hackernews" in platforms:
        hn_leads = search_hackernews(query)
        all_leads.extend(hn_leads)

    # Deduplicate against existing
    new_leads = [l for l in all_leads if l["url"] not in existing_urls]
    new_leads.sort(key=lambda x: x["score"], reverse=True)

    # Save all leads
    existing.extend(new_leads)
    _save_leads(existing)

    # Try to push to Make.com webhook
    webhook_status = ""
    if new_leads:
        webhook_status = send_to_make_webhook(new_leads)

    # Build WhatsApp report
    hot = [l for l in new_leads if l["score"] >= 60]
    warm = [l for l in new_leads if 30 <= l["score"] < 60]

    if not new_leads:
        return f"Lead hunt done for '{query}'. No new leads found. Total in DB: {len(existing)}"

    lines = [f"LEAD HUNT — {time.strftime('%b %d')}"]
    lines.append(f"Query: {query}")
    lines.append(f"New: {len(new_leads)} | Hot: {len(hot)} | Warm: {len(warm)}")

    for lead in hot[:3]:
        lines.append(f"\nHOT ({lead['score']}/100): {lead['title'][:80]}")
        lines.append(f"  {lead['url']}")

    if warm and not hot:
        for lead in warm[:2]:
            lines.append(f"\nWARM ({lead['score']}/100): {lead['title'][:80]}")
            lines.append(f"  {lead['url']}")

    lines.append(f"\nTotal in DB: {len(existing)}")

    if webhook_status:
        lines.append(f"Make.com: {webhook_status[:80]}")

    return "\n".join(lines)


def setup_make_webhook() -> str:
    """Create a Make.com webhook for lead hunting automation."""
    result = create_webhook("blai-lead-hunter", "Receives lead data from BLAI for CRM/email automation")
    return (
        f"{result}\n\n"
        "To complete setup:\n"
        "1. Go to Make.com\n"
        "2. Create a scenario starting with this webhook\n"
        "3. Add modules: Google Sheets (save lead) + Gmail (send outreach)\n"
        "4. Activate the scenario"
    )


def get_lead_stats() -> str:
    """Get stats on all leads found."""
    leads = _load_leads()
    if not leads:
        return "No leads in database yet. Run a hunt first."

    today = time.strftime("%Y-%m-%d")
    today_leads = [l for l in leads if l.get("date_found") == today]
    hot = [l for l in leads if l["score"] >= 60]
    contacted = [l for l in leads if l.get("outreach_sent")]

    return (
        f"LEAD DATABASE:\n"
        f"Total: {len(leads)}\n"
        f"Today: {len(today_leads)}\n"
        f"Hot (60+): {len(hot)}\n"
        f"Contacted: {len(contacted)}\n"
        f"Pending outreach: {len(hot) - len([l for l in hot if l.get('outreach_sent')])}"
    )


def mark_lead_contacted(url: str) -> str:
    """Mark a lead as contacted."""
    leads = _load_leads()
    for lead in leads:
        if lead["url"] == url:
            lead["outreach_sent"] = True
            lead["contacted_date"] = time.strftime("%Y-%m-%d")
            _save_leads(leads)
            return f"Marked as contacted: {lead['title'][:60]}"
    return "Lead not found in database."


if __name__ == "__main__":
    query = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else None
    print(hunt_leads(query))
