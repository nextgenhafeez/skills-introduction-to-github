#!/usr/bin/env python3
"""
App Promoter Skill — Automate organic promotion of Abdul Hafeez's iOS apps.
Picks an app, selects a promotion angle, generates platform-optimized content,
and attempts to post via Make.com.
"""

import json
import random
import time
import os
import requests
from pathlib import Path

# Portfolio of apps to promote
APP_PORTFOLIO = [
    {
        "name": "Arriv",
        "id": "6754357636",
        "url": "https://apps.apple.com/us/app/arriv/id6754357636",
        "tagline": "The future of smart travel tracking.",
        "features": ["AI flight tracking", "Travel documents sync", "Smart delays alert"]
    },
    {
        "name": "Zimbi",
        "id": "6752779930",
        "url": "https://apps.apple.com/us/app/zimbi/id6752779930",
        "tagline": "Simple, powerful financial planning.",
        "features": ["Personal budgeting", "Subscription tracker", "Net worth visualization"]
    },
    {
        "name": "Bible Chats",
        "id": "6752779426",
        "url": "https://apps.apple.com/us/app/bible-chats/id6752779426",
        "tagline": "Engage with scripture like never before.",
        "features": ["Interactive Bible study", "Personal prayer journal", "Community chats"]
    },
    {
        "name": "Catering By Feng",
        "id": "6749269303",
        "url": "https://apps.apple.com/us/app/catering-by-feng/id6749269303",
        "tagline": "Authentic catering, simplified.",
        "features": ["Menu planning", "Direct ordering", "Event coordination"]
    },
    {
        "name": "SakeenaTime",
        "id": "6759330106",
        "url": "https://apps.apple.com/us/app/sakeenatime/id6759330106",
        "tagline": "Your daily companion for peace and mindfulness.",
        "features": ["Guided meditation", "Atmospheric sounds", "Focus timers"]
    }
]

PROMO_ANGLES = [
    "feature_spotlight",
    "founder_story",
    "problem_solution",
    "efficiency_hack",
    "indie_dev_journey",
    "user_testimonial_style",
    "behind_the_scenes"
]

ROOT = Path(__file__).resolve().parent.parent
MEMORY_DIR = ROOT / "memory"
API_KEYS_FILE = ROOT / "config/api_keys.json"

def _load_brain():
    """Import brain selectively to avoid circular imports."""
    import sys
    sys.path.insert(0, str(ROOT))
    from src.brain import think_simple
    return think_simple

def pick_app_and_angle(app_name: str = None) -> tuple:
    """Select randomly or pick a specific app."""
    if app_name:
        app = next((a for a in APP_PORTFOLIO if a["name"].lower() == app_name.lower()), None)
        if not app:
            app = random.choice(APP_PORTFOLIO)
    else:
        app = random.choice(APP_PORTFOLIO)
    
    angle = random.choice(PROMO_ANGLES)
    return app, angle

def generate_promo_content(app: dict, angle: str, platforms: list) -> dict:
    """Generate platform-optimized content using the brain."""
    think_simple = _load_brain()
    
    prompt = f"""
    Create highly engaging, founder-authentic promotion content for my iOS app: {app['name']}.
    Tagline: {app['tagline']}
    Features: {', '.join(app['features'])}
    App Link: {app['url']}
    
    Angle for this post: {angle}
    
    Platforms needed: {', '.join(platforms)}
    
    Guidelines:
    - Don't sound like a 'brand'. Sound like the founder (Abdul Hafeez).
    - Use relevant emojis.
    - For Twitter: Short, punchy, threads if needed.
    - For LinkedIn: Professional, story-driven, 'building in public' style.
    - For Instagram: Visual-first, concise captions.
    - ALWAYS include the app link.
    
    Return the content in JSON format like: {{"twitter": "...", "linkedin": "...", ...}}
    Return ONLY the JSON.
    """
    
    raw_content = think_simple(prompt)
    try:
        # Clean up JSON if it has markdown wrappers
        clean_json = raw_content.strip()
        if "```json" in clean_json:
            clean_json = clean_json.split("```json")[1].split("```")[0].strip()
        elif "```" in clean_json:
            clean_json = clean_json.split("```")[1].split("```")[0].strip()
            
        return json.loads(clean_json)
    except Exception as e:
        print(f"Error parsing promo JSON: {e}")
        # Fallback to simple generation
        results = {}
        for p in platforms:
            results[p] = f"Check out my app {app['name']}! {app['tagline']} {app['url']}"
        return results

def get_available_platforms() -> list:
    """Check config to see which social platforms have webhooks."""
    if not API_KEYS_FILE.exists():
        return ["twitter", "linkedin", "facebook", "instagram"]
    
    try:
        with open(API_KEYS_FILE, 'r') as f:
            config = json.load(f)
            wh_platforms = set()
            for key, val in config.get("make_com", {}).get("webhooks", {}).items():
                platforms = val.get("platforms", [])
                for p in platforms:
                    wh_platforms.add(p)
            return list(wh_platforms) if wh_platforms else ["twitter", "linkedin", "facebook", "instagram"]
    except:
        return ["twitter", "linkedin", "facebook", "instagram"]

def promote_my_app(app_name: str = None) -> str:
    """Full pipeline: Pick -> Generate -> Post."""
    app, angle = pick_app_and_angle(app_name)
    platforms = get_available_platforms()
    
    contents = generate_promo_content(app, angle, platforms)
    
    # Trigger social poster real
    import sys
    sys.path.insert(0, str(ROOT))
    from skills.social_poster_real import post_to_all
    
    results = post_to_all(contents)
    
    summary = f"🚀 *App Promotion Triggered!*\n\n"
    summary += f"App: {app['name']}\n"
    summary += f"Angle: {angle.replace('_', ' ').title()}\n\n"
    summary += results
    
    return summary

def list_apps() -> str:
    """Retrieve the app portfolio links."""
    lines = ["📱 *Abdul Hafeez's App Portfolio:*"]
    for app in APP_PORTFOLIO:
        lines.append(f"- *{app['name']}*: {app['url']}")
    return "\n".join(lines)

if __name__ == "__main__":
    # Test picker
    a, ang = pick_app_and_angle()
    print(f"Testing App Promoter with {a['name']} ({ang})")
    # print(promote_my_app())
