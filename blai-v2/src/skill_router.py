"""
Skill Router — Loads reference skill knowledge AND dispatches to real executable skills.
Reference skills = .md files with knowledge/instructions (~3KB each).
Real skills = Python modules that actually DO things (Make.com, email, social posting).
"""

import os
import importlib
from pathlib import Path

SKILLS_DIR = Path(__file__).parent.parent / "reference-skills"
REAL_SKILLS_DIR = Path(__file__).parent.parent / "skills"

# Keyword → reference skill file mapping (knowledge injection)
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
    "trending": "SKILL-content-engine.md",
    "btc": "SKILL-crypto-intel.md",
    "bitcoin": "SKILL-crypto-intel.md",
    "eth": "SKILL-crypto-intel.md",
    "ethereum": "SKILL-crypto-intel.md",
    "crypto": "SKILL-crypto-intel.md",
    "binance": "SKILL-crypto-intel.md",
    "saylor": "SKILL-crypto-intel.md",
    "hayes": "SKILL-crypto-intel.md",
    "funding": "SKILL-crypto-intel.md",
    "etf": "SKILL-crypto-intel.md",
    "trade": "SKILL-crypto-intel.md",
    "signal": "SKILL-crypto-intel.md",

    "trend": "SKILL-content-engine.md",
    "promote": "SKILL-content-engine.md",
    "comments": "SKILL-content-engine.md",
    "draft": "SKILL-content-engine.md",

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

    # Automation & Make.com
    "automate": "SKILL-n8n-automation.md",
    "make.com": "SKILL-n8n-automation.md",
    "make com": "SKILL-n8n-automation.md",
    "webhook": "SKILL-n8n-automation.md",
    "n8n": "SKILL-n8n-automation.md",
    "scenario": "SKILL-n8n-automation.md",

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

    # App Promotion
    "promote my app": "SKILL-app-promoter.md",
    "promote all apps": "SKILL-app-promoter.md",
    "my app links": "SKILL-app-promoter.md",
    "app links": "SKILL-app-promoter.md",
    "app promoter": "SKILL-app-promoter.md",

    # GitHub Repository Browser
    "github": "SKILL-github-browser.md",
    "repo": "SKILL-github-browser.md",
    "repository": "SKILL-github-browser.md",
    "project code": "SKILL-github-browser.md",
    "client repo": "SKILL-github-browser.md",
    "check on github": "SKILL-github-browser.md",
    "show me the code": "SKILL-github-browser.md",
    "investment platform": "SKILL-github-browser.md",
    "crm": "SKILL-github-browser.md",
    "sushi": "SKILL-github-browser.md",
    "credail": "SKILL-github-browser.md",
}

# Keyword → real executable skill (Python module.function)
# These actually DO things — call APIs, send emails, post content
REAL_SKILL_MAP = {
    # Make.com management + monitoring
    "list scenarios": ("make_com", "monitor"),
    "list make scenarios": ("make_com", "monitor"),
    "show scenarios": ("make_com", "monitor"),
    "scenarios status": ("make_com", "monitor"),
    "run scenario": ("make_com", "run_scenario"),
    "make.com status": ("make_com", "monitor"),
    "make com status": ("make_com", "monitor"),
    "make status": ("make_com", "monitor"),
    "make.com health": ("make_com", "monitor"),
    "make health": ("make_com", "monitor"),
    "monitor make.com": ("make_com", "monitor"),
    "check make.com": ("make_com", "monitor"),
    "make.com errors": ("make_com", "monitor"),
    "any errors on make": ("make_com", "monitor"),
    "is make working": ("make_com", "monitor"),
    "what is broken on make": ("make_com", "monitor"),
    "list webhooks": ("make_com", "list_webhooks"),
    "create webhook": ("make_com", "create_webhook"),

    # Real lead hunting
    "hunt leads": ("lead_hunter_real", "hunt_leads"),
    "find leads": ("lead_hunter_real", "hunt_leads"),
    "lead stats": ("lead_hunter_real", "get_lead_stats"),
    "lead report": ("lead_hunter_real", "get_lead_stats"),
    "setup lead webhook": ("lead_hunter_real", "setup_make_webhook"),

    # Real email outreach
    "send outreach": ("email_outreach", "send_ai_outreach"),
    "outreach stats": ("email_outreach", "get_outreach_stats"),
    "email stats": ("email_outreach", "get_outreach_stats"),
    "setup email webhook": ("email_outreach", "setup_email_webhook"),


    # Real video generation (Kling AI)
    "generate video": ("kling_video", "generate_and_wait"),
    "make video": ("kling_video", "generate_and_wait"),
    "create video": ("kling_video", "generate_and_wait"),
    "text to video": ("kling_video", "generate_and_wait"),
    "video from prompt": ("kling_video", "generate_and_wait"),
    "animate image": ("kling_video", "generate_and_wait"),
    "image to video": ("kling_video", "generate_and_wait"),
    "animate this": ("kling_video", "generate_and_wait"),
    "bring to life": ("kling_video", "generate_and_wait"),
    "kling status": ("kling_video", "list_recent_tasks"),
    "video stats": ("kling_video", "list_recent_tasks"),
    "list videos": ("kling_video", "list_recent_tasks"),


    # Trending intelligence
    "trending": ("trending", "get_trending_digest"),
    "what is trending": ("trending", "get_trending_digest"),
    "whats trending": ("trending", "get_trending_digest"),
    "trends": ("trending", "get_trending_digest"),
    "trending now": ("trending", "get_trending_digest"),
    "tech trends": ("trending", "get_trending_digest"),

    # Project registry
    "list projects": ("project_registry", "list_projects"),
    "show projects": ("project_registry", "list_projects"),
    "what projects": ("project_registry", "list_projects"),
    "register projects": ("project_registry", "bootstrap_from_identity"),
    "next project to promote": ("project_registry", "pick_next_to_promote"),

    # Content strategist
    "draft post": ("content_strategist", "draft_post"),
    "draft daily": ("content_strategist", "draft_daily_batch"),
    "draft daily batch": ("content_strategist", "draft_daily_batch"),
    "daily content": ("content_strategist", "draft_daily_batch"),
    "promote blacklayers": ("content_strategist", "draft_post"),
    "promote website": ("content_strategist", "draft_post"),
    "list drafts": ("content_strategist", "list_drafts"),
    "show drafts": ("content_strategist", "list_drafts"),

    # Comment engine
    "check comments": ("comment_engine", "list_comments_inbox"),
    "comments inbox": ("comment_engine", "list_comments_inbox"),
    "review comments": ("comment_engine", "list_comments_inbox"),
    "draft reply": ("comment_engine", "draft_reply"),
    "pending replies": ("comment_engine", "list_pending_replies"),
    "comment drafts": ("comment_engine", "list_pending_replies"),


    # Real crypto intelligence
    "crypto briefing": ("crypto_intel", "get_full_briefing"),
    "market briefing": ("crypto_intel", "get_full_briefing"),
    "crypto status": ("crypto_intel", "get_full_briefing"),
    "btc status": ("crypto_intel", "get_full_briefing"),
    "market snapshot": ("crypto_intel", "get_market_snapshot"),
    "btc price": ("crypto_intel", "get_market_snapshot"),
    "eth price": ("crypto_intel", "get_market_snapshot"),
    "guru pulse": ("crypto_intel", "get_guru_pulse"),
    "what saylor": ("crypto_intel", "get_guru_pulse"),
    "what hayes": ("crypto_intel", "get_guru_pulse"),
    "etf flows": ("crypto_intel", "get_etf_flows"),
    "btc etf": ("crypto_intel", "get_etf_flows"),
    "funding rate": ("crypto_intel", "get_funding_rate"),
    "btc funding": ("crypto_intel", "get_funding_rate"),
    "macro context": ("crypto_intel", "get_macro_context"),
    "dxy": ("crypto_intel", "get_macro_context"),
    "detect setup": ("crypto_intel", "detect_setups"),
    "any setup": ("crypto_intel", "detect_setups"),
    "trade setup": ("crypto_intel", "detect_setups"),
    "signal scorecard": ("crypto_intel", "get_signal_scorecard"),
    "scorecard": ("crypto_intel", "get_signal_scorecard"),

    # Real social posting
    "post to social": ("social_poster_real", "generate_and_post"),
    "post content": ("social_poster_real", "generate_and_post"),
    "posting stats": ("social_poster_real", "get_posting_stats"),
    "platform status": ("social_poster_real", "list_configured_platforms"),
    "setup social webhook": ("social_poster_real", "setup_platform_webhook"),

    # Real App Promotion
    "promote my app": ("app_promoter", "promote_my_app"),
    "promote all apps": ("app_promoter", "promote_my_app"),
    "my app links": ("app_promoter", "list_apps"),
    "app promo stats": ("social_poster_real", "get_posting_stats"),

    # GitHub Repository Browser
    "list my repos": ("github_browser", "list_repos"),
    "list repos": ("github_browser", "list_repos"),
    "show my repos": ("github_browser", "list_repos"),
    "repo info": ("github_browser", "get_repo_info"),
    "tell me about repo": ("github_browser", "get_repo_info"),
    "show files": ("github_browser", "list_repo_files"),
    "repo files": ("github_browser", "list_repo_files"),
    "read file": ("github_browser", "read_file"),
    "show file": ("github_browser", "read_file"),
    "repo readme": ("github_browser", "get_readme"),
    "search repo": ("github_browser", "search_repo"),
    "search code": ("github_browser", "search_repo"),
    "summarise project": ("github_browser", "summarise_project"),
    "summarize project": ("github_browser", "summarise_project"),
    "project summary": ("github_browser", "summarise_project"),
    "client repos": ("github_browser", "get_client_repos"),
    "check on github": ("github_browser", "summarise_project"),
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


def find_real_skill(message: str) -> tuple:
    """
    Check if a message should trigger a real executable skill.
    Returns (module_name, function_name) or (None, None).
    """
    message_lower = message.lower()

    # Check longest keywords first to avoid partial matches
    sorted_keywords = sorted(REAL_SKILL_MAP.keys(), key=len, reverse=True)
    for keyword in sorted_keywords:
        if keyword in message_lower:
            return REAL_SKILL_MAP[keyword]

    return None, None


def execute_real_skill(module_name: str, function_name: str, **kwargs) -> str:
    """
    Import and execute a real skill function.
    Returns the result string or an error message.
    """
    try:
        import sys
        skills_dir = str(REAL_SKILLS_DIR.parent)
        if skills_dir not in sys.path:
            sys.path.insert(0, skills_dir)

        module = importlib.import_module(f"skills.{module_name}")
        func = getattr(module, function_name)
        result = func(**kwargs) if kwargs else func()
        return result
    except Exception as e:
        return f"Skill error ({module_name}.{function_name}): {e}"
