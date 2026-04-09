#!/usr/bin/env python3
"""
BLAI Scheduler — Runs daily tasks automatically.
Called by cron at specific times.
"""

import sys
import os
import json
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from skills.market_intel import generate_morning_brief, generate_rich_brain_analysis
from skills.lead_hunter import run_hunt, generate_report as lead_report
from skills.social_poster import create_and_post
from skills.email_manager import read_inbox
from skills.daily_improver import generate_scorecard, weekly_review


def send_whatsapp(phone: str, message: str):
    """Queue WhatsApp message for the running bot to send."""
    from src.send_whatsapp import queue_message
    queue_message(phone, message)
    print(f"[Scheduler] Queued message to {phone}: {message[:80]}...")


def task_morning_brief():
    """7 AM — Morning market brief."""
    brief = generate_morning_brief()
    send_whatsapp("212641503230", brief)
    print(brief)


def task_rich_brain():
    """7:30 AM — Rich brain institutional analysis."""
    analysis = generate_rich_brain_analysis()
    send_whatsapp("212641503230", analysis)
    print(analysis)


def task_content():
    """9 AM — Create and post content to all platforms."""
    result = create_and_post()
    topic = result.get("content", {}).get("topic", "unknown")
    results = result.get("results", {})
    msg = f"Content posted — {topic}\n" + "\n".join(f"  {p}: {s}" for p, s in results.items())
    send_whatsapp("212641503230", msg)
    print(msg)


def task_leads():
    """10 AM — Hunt leads and report."""
    results = run_hunt()
    report = lead_report(results)
    send_whatsapp("212641503230", report)
    print(report)


def task_email_check():
    """2 PM — Check emails and summarize."""
    emails = read_inbox(10)
    if emails:
        msg = f"Email check — {len(emails)} new\n"
        for e in emails[:3]:
            msg += f"  From: {e['from'][:30]} — {e['subject'][:40]}\n"
        send_whatsapp("212641503230", msg)
        print(msg)
    else:
        print("No new emails.")


def task_evening_market():
    """6 PM — Evening market update."""
    brief = generate_morning_brief()  # Reuse same function
    send_whatsapp("212641503230", f"Evening update:\n{brief}")
    print(brief)


def task_scorecard():
    """10 PM — Daily scorecard."""
    card = generate_scorecard()
    send_whatsapp("212641503230", card)
    print(card)


def task_weekly():
    """Sunday — Weekly review."""
    review = weekly_review()
    send_whatsapp("212641503230", review)
    print(review)


TASKS = {
    "morning": task_morning_brief,
    "richbrain": task_rich_brain,
    "content": task_content,
    "leads": task_leads,
    "email": task_email_check,
    "evening": task_evening_market,
    "scorecard": task_scorecard,
    "weekly": task_weekly,
}


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 scheduler.py <task>")
        print(f"Tasks: {', '.join(TASKS.keys())}")
        sys.exit(1)

    task_name = sys.argv[1]
    if task_name in TASKS:
        print(f"[Scheduler] Running: {task_name}")
        TASKS[task_name]()
    else:
        print(f"Unknown task: {task_name}")
        sys.exit(1)
