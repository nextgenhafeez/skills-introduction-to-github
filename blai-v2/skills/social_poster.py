#!/usr/bin/env python3
"""
Social Media Poster — Create unique content per platform and post via Make.com webhooks.
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

# Make.com webhooks (update with your actual webhook URLs)
WEBHOOKS = {
    "twitter": os.environ.get("MAKE_TWITTER_WEBHOOK", ""),
    "linkedin": os.environ.get("MAKE_LINKEDIN_WEBHOOK", ""),
    "instagram": os.environ.get("MAKE_INSTAGRAM_WEBHOOK", ""),
}


def generate_content(topic: str = None) -> dict:
    """Generate unique content for each platform about a topic."""

    if not topic:
        topic_prompt = """Pick ONE topic for today's Black Layers social media posts.
Choose from: iOS dev tips, app development cost insights, portfolio showcase (AdClose/$10K month, Sakeena, VooConnect), founder journey, startup advice, AI in mobile apps.
Reply with ONLY the topic in 5 words or less."""
        topic = think_simple(topic_prompt) or "iOS development tips"

    prompt = f"""Create social media posts about: {topic}
For Black Layers (iOS dev company, 20+ apps, AdClose $10K/month).

Write 3 COMPLETELY DIFFERENT versions:

TWITTER (max 280 chars, punchy, 2-3 hashtags):
[tweet here]

LINKEDIN (professional story, 100-150 words, personal angle, 3-5 hashtags):
[post here]

INSTAGRAM (casual, visual-first caption, emojis OK, 15 hashtags):
[caption here]

Each MUST be unique — different hook, different angle, different structure.
Sound like a real founder sharing experience, not a brand account."""

    content = think_simple(prompt)
    if not content:
        return {}

    # Parse the content into platform-specific posts
    result = {"topic": topic, "raw": content, "date": time.strftime("%Y-%m-%d")}

    # Simple parsing — extract sections
    sections = content.split("LINKEDIN")
    if len(sections) >= 2:
        result["twitter"] = sections[0].replace("TWITTER", "").strip().strip(":").strip()
        remaining = sections[1].split("INSTAGRAM")
        result["linkedin"] = remaining[0].strip().strip(":").strip()
        if len(remaining) >= 2:
            result["instagram"] = remaining[1].strip().strip(":").strip()

    return result


def post_to_webhook(platform: str, content: str) -> bool:
    """Post content via Make.com webhook."""
    webhook_url = WEBHOOKS.get(platform, "")
    if not webhook_url:
        return False

    try:
        resp = requests.post(webhook_url, json={
            "platform": platform,
            "content": content,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S")
        }, timeout=15)
        return resp.status_code == 200
    except:
        return False


def create_and_post(topic: str = None) -> dict:
    """Generate content and post to all platforms."""
    content = generate_content(topic)
    if not content:
        return {"error": "Failed to generate content"}

    results = {}
    for platform in ["twitter", "linkedin", "instagram"]:
        text = content.get(platform, "")
        if text:
            posted = post_to_webhook(platform, text)
            results[platform] = "posted" if posted else "webhook not configured"

    # Log
    MEMORY_DIR.mkdir(parents=True, exist_ok=True)
    log_file = MEMORY_DIR / "content_log.json"
    logs = []
    if log_file.exists():
        logs = json.loads(log_file.read_text())
    logs.append({
        "date": time.strftime("%Y-%m-%d"),
        "topic": content.get("topic", ""),
        "results": results
    })
    log_file.write_text(json.dumps(logs[-60:], indent=2))

    return {"content": content, "results": results}


def generate_report() -> str:
    """Quick report for WhatsApp."""
    result = create_and_post()
    if "error" in result:
        return result["error"]

    topic = result["content"].get("topic", "unknown")
    lines = [f"Content created — {topic}"]
    for platform, status in result.get("results", {}).items():
        lines.append(f"  {platform}: {status}")
    return "\n".join(lines)


if __name__ == "__main__":
    import sys
    topic = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else None
    print(generate_report())
