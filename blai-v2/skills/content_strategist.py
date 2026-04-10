"""
BLAI skill: content strategist.

Combines real trending data + project registry + Black Layers brand voice
into platform-specific content drafts. The drafts are SAVED to
memory/content_drafts/<timestamp>.json so Boss can review before they go out.

It does NOT post directly. Posting is delegated to social_poster_real
(which already talks to Make.com webhooks). The strategist only generates,
saves, and queues drafts.

Two main entrypoints used by the skill router:
  - draft_post(focus, platform="twitter") -> str
      Focus may be "blacklayers" (promote the website), a project slug
      (promote that specific project), or "trend" (react to current trends).
  - draft_daily_batch() -> str
      Pulls trending, picks the right mix, generates 4 drafts (Twitter,
      LinkedIn, Instagram caption, blog hook) and saves them all.

Honest about what it can and cannot do:
  - It generates DRAFTS, not finished posts.
  - It calls our internal LLM via brain.think_simple() so the cost rides
    on the same provider state machine.
  - On LLM failure it returns the literal error string, never a fake post.
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

# Skills imported lazily inside functions to avoid circular imports
DRAFTS_DIR = ROOT / "memory" / "content_drafts"
DRAFTS_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = ROOT / "memory" / "content_strategist_log.json"


def _log(entry: dict):
    entry["ts"] = time.strftime("%Y-%m-%dT%H:%M:%S")
    log = []
    if LOG_FILE.exists():
        try:
            log = json.loads(LOG_FILE.read_text())
        except Exception:
            log = []
    log.append(entry)
    log = log[-100:]
    LOG_FILE.write_text(json.dumps(log, indent=2, ensure_ascii=False))


def _load_brand_voice() -> dict:
    """Pull brand voice + key messages from identity.json."""
    try:
        ident = json.loads((ROOT / "config" / "identity.json").read_text())
    except Exception:
        return {}
    return {
        "brand_voice": ident.get("brandVoice", {}),
        "company": ident.get("company", {}),
        "agent": ident.get("agent", {}),
    }


PLATFORM_RULES = {
    "twitter": {
        "max_chars": 280,
        "style": "Short, punchy, hashtag-heavy. 1-3 hashtags max. No corporate jargon. Use line breaks for rhythm. End with a hook or CTA.",
        "include_url": True,
    },
    "linkedin": {
        "max_chars": 1500,
        "style": "Professional storytelling. Open with a hook (number, contrarian take, or short story). Body: 100-200 words of real insight. Close with a question or CTA. 3-5 hashtags at the end. Include blacklayers.ca naturally.",
        "include_url": True,
    },
    "instagram": {
        "max_chars": 2000,
        "style": "Visual-first. First line is the hook. Body explains the value. Casual, emojis OK but sparingly. End with 15-20 niche hashtags grouped at the bottom.",
        "include_url": False,
    },
    "blog": {
        "max_chars": 600,
        "style": "Just generate the title + opening hook + 3-bullet outline (not the full post). The full post will be expanded later.",
        "include_url": True,
    },
}


def _build_prompt(focus: str, platform: str, trending_summary: str, project: dict | None) -> str:
    rules = PLATFORM_RULES.get(platform, PLATFORM_RULES["twitter"])
    brand = _load_brand_voice()
    voice = brand.get("brand_voice", {})
    do = "; ".join(voice.get("do", [])[:5])
    dont = "; ".join(voice.get("dont", [])[:5])
    key_msgs = " | ".join(voice.get("keyMessages", [])[:3])
    company = brand.get("company", {})
    portfolio_blurb = ", ".join(f"{k} ({v[:50]})" for k, v in list(company.get("portfolio", {}).items())[:5])

    project_block = ""
    if project:
        project_block = (
            "\nPROMOTE THIS SPECIFIC PROJECT:\n"
            f"  name: {project.get('name')}\n"
            f"  blurb: {project.get('blurb')}\n"
            f"  highlights: {', '.join(project.get('highlights', []))}\n"
            f"  url: {project.get('url') or '(no public url, mention by name only)'}\n"
        )

    return (
        f"You are drafting a {platform.upper()} post for Black Layers, an iOS app development "
        f"company by Abdul Hafeez (blacklayers.ca).\n\n"
        f"GOAL: {focus}\n\n"
        f"PLATFORM RULES:\n"
        f"  - Max {rules['max_chars']} characters\n"
        f"  - Style: {rules['style']}\n"
        f"  - Include blacklayers.ca: {rules['include_url']}\n\n"
        f"BRAND VOICE — DO: {do}\n"
        f"BRAND VOICE — DON'T: {dont}\n"
        f"KEY MESSAGES: {key_msgs}\n"
        f"PORTFOLIO context: {portfolio_blurb}\n"
        f"{project_block}\n"
        f"REAL CURRENT TRENDS (use to make the post relevant TODAY, do not invent trends):\n"
        f"{trending_summary[:1500]}\n\n"
        f"OUTPUT: Just the post text — no preamble, no 'Here is the draft:', no quotes around it. "
        f"If you cannot fit the goal into the platform's character limit, prioritize the hook + CTA "
        f"and drop the middle. Never invent stats, dates, projects, or client names that are not in "
        f"the brand info above."
    )


def _save_draft(platform: str, focus: str, body: str, source_project: str | None = None) -> str:
    ts = time.strftime("%Y%m%d_%H%M%S")
    fname = f"{ts}_{platform}_{focus[:20]}.json"
    out_path = DRAFTS_DIR / fname
    out_path.write_text(json.dumps({
        "ts": ts,
        "platform": platform,
        "focus": focus,
        "source_project": source_project,
        "body": body,
        "status": "draft",
    }, indent=2, ensure_ascii=False))
    return str(out_path)


def draft_post(focus: str = "trend", platform: str = "twitter") -> str:
    """
    Generate one platform-specific draft.

    focus values:
      - "blacklayers"  → promote blacklayers.ca itself (services / hiring CTA)
      - "<project-slug>" → promote a specific project from the registry
      - "trend"        → react to a current trending topic
    """
    from skills import trending as t
    from skills import project_registry as pr
    from src import brain

    project = None
    if focus not in ("blacklayers", "trend"):
        project = pr.get_project(focus)
        if not project:
            return (
                f"No project '{focus}' found in registry. Use list_projects to see "
                f"options, or focus on 'blacklayers' or 'trend'."
            )

    trending_summary = t.get_trending_digest()

    prompt = _build_prompt(focus, platform, trending_summary, project)

    try:
        draft_body = brain.think_simple(prompt) or ""
    except Exception as e:
        return f"LLM call failed: {e}"

    if not draft_body.strip():
        return "LLM returned empty — both Gemini and Groq are unavailable. Try again later."

    saved_path = _save_draft(platform, focus, draft_body, source_project=focus if project else None)
    if project:
        pr.mark_promoted(project["slug"])
    _log({"op": "draft_post", "platform": platform, "focus": focus, "saved": saved_path})

    return (
        f"Draft generated for {platform.upper()} ({focus}):\n\n"
        f"{draft_body}\n\n"
        f"Saved to: {saved_path}\n"
        f"To post it: 'post draft {Path(saved_path).stem}' or send to social_poster_real."
    )


def draft_daily_batch() -> str:
    """Generate one draft per platform (4 total) tied to today's trending data."""
    from skills import project_registry as pr

    pr.bootstrap_from_identity()
    next_proj = pr.pick_next_to_promote()
    project_focus = next_proj["slug"] if next_proj else "blacklayers"

    plan = [
        ("twitter",  "trend"),         # one trend reaction
        ("linkedin", project_focus),   # one project showcase
        ("instagram", "blacklayers"),  # one brand visibility
        ("blog",     "trend"),         # one blog hook from trend
    ]

    results = []
    for platform, focus in plan:
        out = draft_post(focus=focus, platform=platform)
        results.append(f"---- {platform.upper()} ({focus}) ----\n{out[:500]}\n")

    return "Daily batch generated:\n\n" + "\n".join(results)


def list_drafts(limit: int = 10) -> str:
    files = sorted(DRAFTS_DIR.glob("*.json"), reverse=True)[:limit]
    if not files:
        return "No drafts in memory/content_drafts/ yet."
    lines = [f"Last {len(files)} drafts:"]
    for f in files:
        try:
            d = json.loads(f.read_text())
            lines.append(
                f"- {f.stem}  [{d.get('platform','?')}/{d.get('focus','?')}]  "
                f"{d.get('body','')[:80]}..."
            )
        except Exception:
            continue
    return "\n".join(lines)
