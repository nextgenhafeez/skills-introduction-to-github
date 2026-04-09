"""
Skill Router — Loads the right OpenClaw skill knowledge on demand.
Instead of loading ALL 24 skills (68KB), loads only what's needed (~3KB).
"""

import os
from pathlib import Path

SKILLS_DIR = Path(__file__).parent.parent / "reference-skills"

# Keyword → skill file mapping
SKILL_MAP = {
    # Lead hunting & outreach
    "lead": "SKILL-lead-hunter.md",
    "client": "SKILL-lead-hunter.md",
    "prospect": "SKILL-lead-hunter.md",
    "outreach": "SKILL-lead-hunter.md",
    "find me": "SKILL-lead-hunter.md",
    "hunt": "SKILL-lead-hunter.md",

    # Content & social media
    "post": "SKILL-content-engine.md",
    "content": "SKILL-content-engine.md",
    "tweet": "SKILL-twitter-manager.md",
    "twitter": "SKILL-twitter-manager.md",
    "linkedin": "SKILL-linkedin-manager.md",
    "instagram": "SKILL-content-engine.md",
    "tiktok": "SKILL-tiktok-realistic-video.md",
    "social media": "SKILL-content-engine.md",
    "blog": "SKILL-content-engine.md",

    # Video & image
    "video": "SKILL-video-creator.md",
    "kling": "SKILL-kling-video.md",
    "image": "SKILL-image-creator.md",
    "graphic": "SKILL-image-creator.md",
    "thumbnail": "SKILL-image-creator.md",
    "reel": "SKILL-viral-video-ai.md",
    "short": "SKILL-viral-video-ai.md",
    "viral": "SKILL-viral-video-ai.md",

    # Crypto & trading
    "crypto": "SKILL-crypto-research.md",
    "bitcoin": "SKILL-crypto-research.md",
    "btc": "SKILL-crypto-research.md",
    "eth": "SKILL-crypto-research.md",
    "market": "SKILL-crypto-research.md",
    "trade": "SKILL-binance-trading.md",
    "binance": "SKILL-binance-trading.md",
    "buy": "SKILL-crypto-research.md",
    "sell": "SKILL-crypto-research.md",
    "fear": "SKILL-crypto-research.md",
    "whale": "SKILL-crypto-research.md",
    "blackrock": "SKILL-crypto-research.md",
    "buffett": "SKILL-crypto-research.md",
    "rothschild": "SKILL-crypto-research.md",

    # Brand & identity
    "brand": "SKILL-brand-identity.md",
    "black layers": "SKILL-brand-identity.md",
    "portfolio": "SKILL-brand-identity.md",
    "adclose": "SKILL-brand-identity.md",
    "sakeena": "SKILL-brand-identity.md",

    # Code & development
    "code": "SKILL-code-developer.md",
    "swift": "SKILL-code-developer.md",
    "xcode": "SKILL-code-developer.md",
    "app": "SKILL-code-developer.md",
    "bug": "SKILL-code-developer.md",
    "debug": "SKILL-code-developer.md",
    "react": "SKILL-code-developer.md",
    "python": "SKILL-code-developer.md",

    # Analytics & reporting
    "analytics": "SKILL-analytics-reporter.md",
    "report": "SKILL-analytics-reporter.md",
    "numbers": "SKILL-analytics-reporter.md",
    "growth": "SKILL-analytics-reporter.md",
    "engagement": "SKILL-analytics-reporter.md",
    "scorecard": "SKILL-daily-scorecard.md",

    # Automation
    "automate": "SKILL-n8n-automation.md",
    "make.com": "SKILL-n8n-automation.md",
    "webhook": "SKILL-n8n-automation.md",
    "n8n": "SKILL-n8n-automation.md",

    # Self improvement
    "improve": "SKILL-self-improver.md",
    "upgrade": "SKILL-ai-self-upgrade.md",
    "learn": "SKILL-self-improver.md",

    # Trending
    "trend": "SKILL-trend-tracker.md",
    "trending": "SKILL-trend-tracker.md",
    "what's new": "SKILL-trend-tracker.md",

    # File delivery
    "send file": "SKILL-file-delivery.md",
    "deliver": "SKILL-file-delivery.md",
    "scp": "SKILL-file-delivery.md",

    # Daily tasks
    "schedule": "SKILL-daily-tasks.md",
    "routine": "SKILL-daily-tasks.md",
    "daily": "SKILL-daily-tasks.md",
    "what did you do": "SKILL-daily-scorecard.md",
}


def find_relevant_skills(message: str, max_skills: int = 2) -> str:
    """
    Given a user message, find and load the most relevant skill files.
    Returns the skill content as a string to inject into the prompt.
    Max 2 skills loaded per message to keep tokens low.
    """
    message_lower = message.lower()
    matched_files = set()

    for keyword, skill_file in SKILL_MAP.items():
        if keyword in message_lower:
            matched_files.add(skill_file)
            if len(matched_files) >= max_skills:
                break

    if not matched_files:
        return ""

    skill_content = []
    for skill_file in matched_files:
        filepath = SKILLS_DIR / skill_file
        if filepath.exists():
            content = filepath.read_text()
            # Truncate to 2000 chars per skill to keep tokens reasonable
            if len(content) > 2000:
                content = content[:2000] + "\n...(truncated)"
            skill_content.append(f"--- {skill_file} ---\n{content}")

    if skill_content:
        return "\n\nRELEVANT SKILL KNOWLEDGE:\n" + "\n".join(skill_content)

    return ""
