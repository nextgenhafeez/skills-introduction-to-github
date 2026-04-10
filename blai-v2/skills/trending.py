"""
BLAI skill: trending intelligence (REAL, not a stub).

Pulls real trending data from public APIs/feeds that the GCP VM can reach:
  - Hacker News  : https://hacker-news.firebaseio.com/v0/
  - Dev.to       : https://dev.to/api/articles
  - GitHub       : https://github.com/trending/<lang>?since=<period>  (HTML)
  - Product Hunt : https://www.producthunt.com/feed                  (RSS)

Reddit is intentionally NOT used: Reddit blocks Google Cloud IPs unless we
set up an OAuth app. If Boss wants Reddit later, we register an app at
https://www.reddit.com/prefs/apps and add the client_id/secret to
config/api_keys.json under reddit_oauth.

Public functions used by the skill router and content_strategist:
  - fetch_trending(topics=None, limit_per_source=5) -> dict
  - get_trending_digest(topics=None) -> str   (human-readable for WhatsApp)
  - match_to_blacklayers(items) -> list       (filters items relevant to BL)

All network errors are caught and surfaced verbatim — never fabricated.
Results are cached for 30 minutes in memory/trending_cache.json so we don't
hammer the APIs and the dashboard / scheduler can call this cheaply.
"""
from __future__ import annotations

import html
import json
import re
import time
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parent.parent
CACHE_FILE = ROOT / "memory" / "trending_cache.json"
LOG_FILE = ROOT / "memory" / "trending_log.json"

CACHE_TTL_SECONDS = 30 * 60  # 30 min — trends move slowly enough

# Topics that map to Black Layers expertise. If a trending item contains any
# of these tokens (case-insensitive), it's flagged as relevant.
BL_KEYWORDS = [
    "ios", "iphone", "ipad", "swift", "swiftui", "objective-c", "xcode",
    "app store", "appstore", "tiktok shop", "in-app purchase", "in app purchase",
    "react native", "react-native", "flutter",
    "ai agent", "agentic", "llm", "gpt", "claude", "gemini",
    "mobile dev", "mobile app", "apple", "vision pro", "macos", "watchos",
    "saas", "indie hacker", "indie dev", "side project", "build in public",
    "fintech", "ad tech", "adtech", "real estate tech", "proptech",
    "ux", "ui", "design system", "freelance",
]

USER_AGENT = "BLAI Content Agent for Black Layers (blacklayers.ca)"


# ---------- Logging ----------

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
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    LOG_FILE.write_text(json.dumps(log, indent=2, ensure_ascii=False))


# ---------- Source: Hacker News ----------

def _fetch_hn(limit: int = 10) -> list:
    """Top stories from HN. Returns [{source, title, url, score, comments}]."""
    out: list = []
    try:
        ids = requests.get(
            "https://hacker-news.firebaseio.com/v0/topstories.json",
            timeout=10,
        ).json()[:limit]
        for sid in ids:
            try:
                item = requests.get(
                    f"https://hacker-news.firebaseio.com/v0/item/{sid}.json",
                    timeout=8,
                ).json()
                if not item or item.get("type") != "story":
                    continue
                out.append({
                    "source": "hackernews",
                    "title": item.get("title", ""),
                    "url": item.get("url") or f"https://news.ycombinator.com/item?id={sid}",
                    "score": item.get("score", 0),
                    "comments": item.get("descendants", 0),
                })
            except Exception:
                continue
    except Exception as e:
        _log({"src": "hn", "error": str(e)[:200]})
    return out


# ---------- Source: GitHub Trending (HTML scrape) ----------

def _fetch_github_trending(language: str = "", since: str = "daily", limit: int = 10) -> list:
    """Scrape github.com/trending/<lang>?since=<period>."""
    url = f"https://github.com/trending/{language}?since={since}" if language else f"https://github.com/trending?since={since}"
    out: list = []
    try:
        r = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=15)
        if r.status_code != 200:
            _log({"src": "github", "http": r.status_code})
            return out
        # Repo titles look like:  <h2 class="h3 lh-condensed"><a href="/owner/name" ...>
        repos = re.findall(
            r'<h2 class="h3 lh-condensed">\s*<a href="(/[^"]+)"',
            r.text,
        )
        # Descriptions:  <p class="col-9 color-fg-muted my-1 pr-4">DESC</p>
        descs = re.findall(
            r'<p class="col-9 color-fg-muted my-1 pr-4">\s*(.+?)\s*</p>',
            r.text,
            flags=re.DOTALL,
        )
        # Star counts (today/this week)
        stars = re.findall(
            r'<span class="d-inline-block float-sm-right">\s*<svg[^>]+star.+?</svg>\s*([\d,]+)',
            r.text,
            flags=re.DOTALL,
        )
        for i, repo_path in enumerate(repos[:limit]):
            out.append({
                "source": "github",
                "title": repo_path.lstrip("/"),
                "url": "https://github.com" + repo_path,
                "description": html.unescape(descs[i].strip()) if i < len(descs) else "",
                "stars_today": stars[i] if i < len(stars) else "",
            })
    except Exception as e:
        _log({"src": "github", "error": str(e)[:200]})
    return out


# ---------- Source: Dev.to ----------

def _fetch_devto(tag: str = "ios", limit: int = 10) -> list:
    """Top dev.to articles for a tag."""
    out: list = []
    try:
        r = requests.get(
            f"https://dev.to/api/articles?tag={tag}&top=1&per_page={limit}",
            headers={"User-Agent": USER_AGENT},
            timeout=10,
        )
        if r.status_code != 200:
            _log({"src": "devto", "http": r.status_code, "tag": tag})
            return out
        for a in r.json()[:limit]:
            out.append({
                "source": "devto",
                "title": a.get("title", ""),
                "url": a.get("url", ""),
                "tag": tag,
                "reactions": a.get("public_reactions_count", 0),
                "comments": a.get("comments_count", 0),
                "description": (a.get("description") or "")[:200],
            })
    except Exception as e:
        _log({"src": "devto", "error": str(e)[:200]})
    return out


# ---------- Source: Product Hunt RSS ----------

def _fetch_producthunt(limit: int = 10) -> list:
    """Latest Product Hunt launches via public RSS."""
    out: list = []
    try:
        r = requests.get(
            "https://www.producthunt.com/feed",
            headers={"User-Agent": USER_AGENT},
            timeout=10,
        )
        if r.status_code != 200:
            _log({"src": "producthunt", "http": r.status_code})
            return out
        # Parse <item><title>...</title><link>...</link><description>...</description>
        items = re.findall(
            r"<item>\s*<title>(.+?)</title>\s*<link>(.+?)</link>\s*<description>(.+?)</description>",
            r.text,
            flags=re.DOTALL,
        )
        for title, link, desc in items[:limit]:
            out.append({
                "source": "producthunt",
                "title": html.unescape(title.strip()),
                "url": link.strip(),
                "description": html.unescape(re.sub(r"<[^>]+>", " ", desc).strip())[:200],
            })
    except Exception as e:
        _log({"src": "producthunt", "error": str(e)[:200]})
    return out


# ---------- Public API ----------

def _is_relevant(item: dict) -> bool:
    blob = " ".join([
        str(item.get("title", "")),
        str(item.get("description", "")),
        str(item.get("tag", "")),
    ]).lower()
    return any(k in blob for k in BL_KEYWORDS)


def match_to_blacklayers(items: list) -> list:
    """Filter items down to ones relevant to Black Layers expertise."""
    return [i for i in items if _is_relevant(i)]


def fetch_trending(topics: list | None = None, limit_per_source: int = 8) -> dict:
    """
    Pull trending content from all available sources, with caching.

    `topics`: optional list of dev.to tags to fetch (default: ios, ai, swift, mobile)
    Returns: {hackernews:[...], github:[...], devto:[...], producthunt:[...],
              relevant:[...] (subset matching BL keywords), fetched_at, cached: bool}
    """
    # Cache check
    if CACHE_FILE.exists():
        try:
            cached = json.loads(CACHE_FILE.read_text())
            if time.time() - cached.get("fetched_at", 0) < CACHE_TTL_SECONDS:
                cached["cached"] = True
                return cached
        except Exception:
            pass

    if not topics:
        topics = ["ios", "ai", "swift", "mobile"]

    hn = _fetch_hn(limit=limit_per_source)
    gh_swift = _fetch_github_trending("swift", limit=limit_per_source)
    gh_ai = _fetch_github_trending("python", limit=limit_per_source)
    devto_items: list = []
    for tag in topics:
        devto_items.extend(_fetch_devto(tag, limit=limit_per_source))
    ph = _fetch_producthunt(limit=limit_per_source)

    all_items = hn + gh_swift + gh_ai + devto_items + ph
    relevant = match_to_blacklayers(all_items)

    out = {
        "fetched_at": int(time.time()),
        "cached": False,
        "hackernews": hn,
        "github_swift": gh_swift,
        "github_python": gh_ai,
        "devto": devto_items,
        "producthunt": ph,
        "relevant": relevant,
        "totals": {
            "hackernews": len(hn),
            "github_swift": len(gh_swift),
            "github_python": len(gh_ai),
            "devto": len(devto_items),
            "producthunt": len(ph),
            "relevant": len(relevant),
        },
    }
    CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
    CACHE_FILE.write_text(json.dumps(out, indent=2, ensure_ascii=False))
    _log({"op": "fetch_trending", "totals": out["totals"]})
    return out


def get_trending_digest(topics: list | None = None) -> str:
    """Human-readable digest for WhatsApp / scheduler. Honest about source counts."""
    data = fetch_trending(topics=topics)
    cached = " (cached)" if data.get("cached") else " (live)"

    lines = [
        f"Trending intelligence digest{cached} — fetched at "
        + time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime(data["fetched_at"])),
        "",
        "Counts: " + ", ".join(f"{k}={v}" for k, v in data["totals"].items()),
        "",
        f"** Top {min(5, len(data['relevant']))} items relevant to Black Layers **",
    ]
    if not data["relevant"]:
        lines.append("  (no items matched Black Layers keywords this cycle)")
    else:
        for i, item in enumerate(data["relevant"][:5], 1):
            t = (item.get("title") or "")[:120]
            src = item.get("source", "?")
            url = item.get("url", "")
            extra = ""
            if item.get("score") is not None:
                extra = f" [{item.get('score', 0)} pts]"
            elif item.get("reactions") is not None:
                extra = f" [{item.get('reactions', 0)} reactions]"
            elif item.get("stars_today"):
                extra = f" [+{item['stars_today']} stars]"
            lines.append(f"  {i}. [{src}]{extra} {t}")
            if url:
                lines.append(f"     {url}")
    lines.append("")
    lines.append("Top non-filtered HN headlines:")
    for h in data["hackernews"][:3]:
        lines.append(f"  - {(h.get('title') or '')[:120]}")
    return "\n".join(lines)
