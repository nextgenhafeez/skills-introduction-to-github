#!/usr/bin/env python3
"""
Daily Improver — Self-grading, learning from mistakes, getting smarter.
"""

import json
import time
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.brain import think_simple
from pathlib import Path

MEMORY_DIR = Path(__file__).parent.parent / "memory"


def collect_today_stats() -> dict:
    """Collect what happened today from all memory files."""
    today = time.strftime("%Y-%m-%d")
    stats = {
        "date": today,
        "posts_created": 0,
        "leads_found": 0,
        "emails_sent": 0,
        "signals_given": 0,
        "errors": []
    }

    # Count content
    content_log = MEMORY_DIR / "content_log.json"
    if content_log.exists():
        logs = json.loads(content_log.read_text())
        stats["posts_created"] = sum(1 for l in logs if l.get("date") == today)

    # Count leads
    leads_file = MEMORY_DIR / "leads.json"
    if leads_file.exists():
        leads = json.loads(leads_file.read_text()).get("leads", [])
        stats["leads_found"] = sum(1 for l in leads if l.get("date_found") == today)

    # Count emails
    email_log = MEMORY_DIR / "email_log.json"
    if email_log.exists():
        logs = json.loads(email_log.read_text())
        stats["emails_sent"] = sum(1 for l in logs if l.get("date", "").startswith(today))

    # Count market signals
    signals_file = MEMORY_DIR / "signals.json"
    if signals_file.exists():
        signals = json.loads(signals_file.read_text())
        stats["signals_given"] = sum(1 for s in signals if s.get("date") == today)

    return stats


def generate_scorecard() -> str:
    """Generate nightly scorecard for WhatsApp."""
    stats = collect_today_stats()

    # Ask AI to grade
    prompt = f"""Grade this AI agent's daily performance (be honest, 1-10):

Stats for {stats['date']}:
- Posts created: {stats['posts_created']}
- Leads found: {stats['leads_found']}
- Emails sent: {stats['emails_sent']}
- Market signals: {stats['signals_given']}

Expected daily targets:
- Posts: 3+ (one per platform)
- Leads: 2+ hot leads
- Emails: 5+ outreach
- Signals: 1 morning brief

Give: grade/10, what went well, what failed, #1 priority for tomorrow.
MAX 8 lines. Be brutally honest."""

    analysis = think_simple(prompt)

    # Save scorecard
    daily_dir = MEMORY_DIR / "daily"
    daily_dir.mkdir(parents=True, exist_ok=True)
    scorecard = {**stats, "analysis": analysis}
    (daily_dir / f"{stats['date']}.json").write_text(json.dumps(scorecard, indent=2))

    # Save to learnings
    learnings_file = MEMORY_DIR / "learnings.json"
    learnings = []
    if learnings_file.exists():
        learnings = json.loads(learnings_file.read_text())
    learnings.append({
        "date": stats["date"],
        "stats": stats,
        "analysis_summary": (analysis or "")[:200]
    })
    learnings_file.write_text(json.dumps(learnings[-30:], indent=2))

    return f"SCORECARD — {stats['date']}\n\nPosts: {stats['posts_created']} | Leads: {stats['leads_found']} | Emails: {stats['emails_sent']}\n\n{analysis or 'Analysis unavailable'}"


def weekly_review() -> str:
    """Sunday weekly review — what worked, what didn't, strategy changes."""
    daily_dir = MEMORY_DIR / "daily"
    if not daily_dir.exists():
        return "No daily data yet for weekly review."

    # Collect last 7 days
    files = sorted(daily_dir.glob("*.json"))[-7:]
    week_data = []
    for f in files:
        week_data.append(json.loads(f.read_text()))

    if not week_data:
        return "No data for weekly review."

    total_posts = sum(d.get("posts_created", 0) for d in week_data)
    total_leads = sum(d.get("leads_found", 0) for d in week_data)
    total_emails = sum(d.get("emails_sent", 0) for d in week_data)

    prompt = f"""Weekly review for BLAI (Black Layers AI agent):

This week's totals:
- Posts: {total_posts}
- Leads: {total_leads}
- Emails: {total_emails}
- Days with data: {len(week_data)}

Give:
1. Overall grade (1-10)
2. What's working
3. What's NOT working
4. Top 3 changes for next week
5. Prediction if we keep this pace

Be honest and specific. MAX 12 lines."""

    return think_simple(prompt) or "Weekly review unavailable."


if __name__ == "__main__":
    print(generate_scorecard())
