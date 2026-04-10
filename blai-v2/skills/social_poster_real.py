#!/usr/bin/env python3
"""
Social Poster Real — Post to social platforms via Make.com webhooks.
Uses preconfigured webhooks for YouTube/Buffer and Facebook/Instagram.
Can create new webhooks for additional platforms.
"""

import json
import time
import requests
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.brain import think_simple
from skills.make_com import (
    call_webhook, call_webhook_by_name, create_webhook,
    _load_webhooks, _get_webhooks_config
)
from pathlib import Path

MEMORY_DIR = Path(__file__).parent.parent / "memory"
POSTS_LOG = MEMORY_DIR / "posts_log.json"

# Platform-specific webhook name mapping
PLATFORM_WEBHOOK_MAP = {
    "youtube": "youtube_buffer",
    "buffer": "youtube_buffer",
    "facebook": "facebook_instagram",
    "instagram": "facebook_instagram",
    "twitter": "twitter",
    "linkedin": "linkedin",
    "tiktok": "tiktok",
}


def _load_posts_log() -> list:
    """Load posts tracking log."""
    if POSTS_LOG.exists():
        return json.loads(POSTS_LOG.read_text())
    return []


def _save_post(entry: dict):
    """Save a post entry to the log."""
    MEMORY_DIR.mkdir(parents=True, exist_ok=True)
    log = _load_posts_log()
    log.append(entry)
    POSTS_LOG.write_text(json.dumps(log[-200:], indent=2))


def _find_webhook_for_platform(platform: str) -> tuple:
    """
    Find the right webhook URL for a platform.
    Returns (url, source_name) or (None, None).
    """
    platform = platform.lower().strip()
    config_wh = _get_webhooks_config()
    saved_wh = _load_webhooks()

    # Check mapped name in config webhooks
    mapped_name = PLATFORM_WEBHOOK_MAP.get(platform, platform)

    if mapped_name in config_wh:
        return config_wh[mapped_name], f"config:{mapped_name}"

    # Check saved webhooks
    for name, info in saved_wh.items():
        if platform in name.lower() or mapped_name in name.lower():
            return info["url"], f"saved:{name}"

    # Check config webhooks with fuzzy match
    for name, url in config_wh.items():
        if platform in name.lower():
            return url, f"config:{name}"

    return None, None


def post_to_social(platform: str, content: str, image_url: str = None) -> str:
    """
    Post content to a social media platform via Make.com webhook.

    Args:
        platform: "youtube", "facebook", "instagram", "twitter", "linkedin", "tiktok"
        content: The post text/caption
        image_url: Optional image URL to include

    Returns: WhatsApp-friendly status message
    """
    platform = platform.lower().strip()
    webhook_url, source = _find_webhook_for_platform(platform)

    if not webhook_url:
        available = list(PLATFORM_WEBHOOK_MAP.keys())
        config_wh = _get_webhooks_config()
        configured = list(config_wh.keys())
        return (
            f"No webhook configured for '{platform}'.\n"
            f"Configured webhooks: {', '.join(configured) or 'none'}\n\n"
            f"To add {platform}:\n"
            f"1. Create a Make.com scenario for {platform}\n"
            f"2. Use: setup_platform_webhook('{platform}')"
        )

    # Build payload
    payload = {
        "platform": platform,
        "content": content,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "source": "BLAI"
    }
    if image_url:
        payload["image_url"] = image_url

    # Send to webhook
    try:
        resp = requests.post(webhook_url, json=payload, timeout=15)

        success = resp.status_code == 200
        status = "posted" if success else f"webhook returned {resp.status_code}"

        # Log the post
        _save_post({
            "platform": platform,
            "content": content[:200],
            "image_url": image_url,
            "date": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "status": status,
            "webhook_source": source
        })

        if success:
            return f"Posted to {platform} via {source}.\nContent: {content[:100]}..."
        else:
            return (
                f"Webhook for {platform} returned {resp.status_code}.\n"
                "The webhook exists but the Make.com scenario may not be active.\n"
                "Check Make.com dashboard to ensure the scenario is ON."
            )

    except Exception as e:
        _save_post({
            "platform": platform,
            "content": content[:200],
            "date": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "status": f"error: {e}",
            "webhook_source": source
        })
        return f"Failed to post to {platform}: {e}"


def post_to_all(content_dict: dict, image_url: str = None) -> str:
    """
    Post different content to multiple platforms.

    Args:
        content_dict: {"twitter": "tweet text", "linkedin": "post text", ...}
        image_url: Optional image URL (sent to all platforms)

    Returns: Summary of results
    """
    results = []
    for platform, content in content_dict.items():
        result = post_to_social(platform, content, image_url)
        results.append(f"{platform}: {result.split(chr(10))[0]}")

    return "POSTING RESULTS:\n" + "\n".join(results)


def generate_and_post(topic: str = None, platforms: list = None) -> str:
    """
    Generate unique content per platform and post it.

    Args:
        topic: What to post about (auto-picks if None)
        platforms: Which platforms (default: all configured)
    """
    if not topic:
        topic_prompt = """Pick ONE topic for Black Layers social media today.
Options: iOS dev tips, app cost insights, portfolio (AdClose $10K/month), founder journey, AI in mobile.
Reply with ONLY the topic in 5 words or less."""
        topic = think_simple(topic_prompt) or "iOS development tips"

    if not platforms:
        # Only include platforms with configured webhooks
        platforms = []
        for p in ["youtube", "facebook", "instagram", "twitter", "linkedin"]:
            url, _ = _find_webhook_for_platform(p)
            if url:
                platforms.append(p)

    if not platforms:
        return (
            "No social media webhooks configured.\n"
            "Set up webhooks in Make.com for your platforms first.\n"
            "Current config webhooks: " + ", ".join(_get_webhooks_config().keys() or ["none"])
        )

    platform_list = ", ".join(platforms)
    prompt = f"""Create social media posts about: {topic}
For Black Layers (iOS dev company, 20+ apps, AdClose $10K/month).

Write a UNIQUE version for each platform:
{chr(10).join(f'{p.upper()}: [write {p}-optimized content]' for p in platforms)}

Each MUST be different — different hook, angle, structure.
Sound like a real founder, not a brand account.
Return ONLY the content, labeled by platform name."""

    content = think_simple(prompt)
    if not content:
        return "Failed to generate content — AI unavailable."

    # Parse content by platform
    content_dict = {}
    current_platform = None
    current_lines = []

    for line in content.split("\n"):
        line_upper = line.strip().upper()
        matched = False
        for p in platforms:
            if line_upper.startswith(p.upper()):
                if current_platform and current_lines:
                    content_dict[current_platform] = "\n".join(current_lines).strip()
                current_platform = p
                # Remove platform label from content
                remainder = line.strip()[len(p):].strip().lstrip(":").strip()
                current_lines = [remainder] if remainder else []
                matched = True
                break
        if not matched and current_platform:
            current_lines.append(line)

    if current_platform and current_lines:
        content_dict[current_platform] = "\n".join(current_lines).strip()

    if not content_dict:
        return f"Generated content but couldn't parse it by platform. Raw:\n{content[:300]}"

    # Post each one
    return post_to_all(content_dict)


def setup_platform_webhook(platform: str) -> str:
    """Create a Make.com webhook for a new platform."""
    result = create_webhook(f"blai-{platform}-poster", f"Posts content to {platform} from BLAI")
    return (
        f"{result}\n\n"
        f"To complete {platform} setup:\n"
        f"1. Go to Make.com\n"
        f"2. Create scenario: Webhook -> {platform.title()} module\n"
        f"3. Map 'content' field to post text, 'image_url' to media\n"
        f"4. Activate the scenario"
    )


def get_posting_stats() -> str:
    """Get social posting statistics."""
    log = _load_posts_log()
    if not log:
        return "No posts tracked yet."

    today = time.strftime("%Y-%m-%d")
    today_posts = [p for p in log if p["date"].startswith(today)]

    by_platform = {}
    for p in log:
        plat = p.get("platform", "unknown")
        by_platform[plat] = by_platform.get(plat, 0) + 1

    successful = [p for p in log if p.get("status") == "posted"]

    lines = [
        f"POSTING STATS:",
        f"Total posts: {len(log)} ({len(successful)} successful)",
        f"Today: {len(today_posts)}",
        "By platform:"
    ]
    for plat, count in sorted(by_platform.items()):
        lines.append(f"  {plat}: {count}")

    # Show configured webhooks
    config_wh = _get_webhooks_config()
    if config_wh:
        lines.append(f"\nActive webhooks: {', '.join(config_wh.keys())}")

    return "\n".join(lines)


def list_configured_platforms() -> str:
    """Show which platforms have webhooks ready."""
    lines = ["PLATFORM STATUS:\n"]
    for platform in ["youtube", "facebook", "instagram", "twitter", "linkedin", "tiktok"]:
        url, source = _find_webhook_for_platform(platform)
        status = f"READY ({source})" if url else "NOT CONFIGURED"
        lines.append(f"  {platform}: {status}")

    return "\n".join(lines)


if __name__ == "__main__":
    print(list_configured_platforms())
    print()
    print(get_posting_stats())
