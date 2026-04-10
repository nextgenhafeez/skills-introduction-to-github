"""
BLAI skill: project registry for promotable Black Layers projects.

The agent needs a single source of truth for "what projects can we publicly
promote and how". This skill manages memory/projects.json so BLAI can:
  - List projects when Boss asks "what should I promote this week?"
  - Add a new project when Boss says "register project X"
  - Pull the right project when content_strategist generates a case-study post
  - Track which projects have been promoted recently (anti-spam)

Schema (projects.json):
{
  "projects": [
    {
      "slug": "adclose",
      "name": "AdClose",
      "type": "iOS app",
      "url": "https://apps.apple.com/.../adclose",
      "client": null,            # null if it's our own product, or client name
      "is_public": true,         # safe to promote publicly?
      "tech": ["Swift", "SwiftUI", "StoreKit"],
      "blurb": "Ad blocker generating $10K+/month",
      "highlights": ["10K+ MRR", "100K+ downloads", "4.8 stars"],
      "screenshots": [],         # list of urls or local paths
      "launched": "2023-08",
      "last_promoted": null,     # ISO timestamp
      "promote_count": 0
    }
  ],
  "updated_at": "..."
}
"""
from __future__ import annotations

import json
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PROJECTS_FILE = ROOT / "memory" / "projects.json"


# ---------- IO ----------

def _load() -> dict:
    if not PROJECTS_FILE.exists():
        return {"projects": [], "updated_at": ""}
    try:
        return json.loads(PROJECTS_FILE.read_text())
    except Exception:
        return {"projects": [], "updated_at": ""}


def _save(data: dict):
    data["updated_at"] = time.strftime("%Y-%m-%dT%H:%M:%S")
    PROJECTS_FILE.parent.mkdir(parents=True, exist_ok=True)
    PROJECTS_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False))


def _slugify(text: str) -> str:
    return "".join(c.lower() if c.isalnum() else "-" for c in (text or "")).strip("-")[:40]


# ---------- Bootstrap from identity.json ----------

def bootstrap_from_identity() -> str:
    """
    Seed projects.json from identity.json's company.portfolio if it's empty.
    Idempotent: only adds projects whose slug isn't already present.
    """
    try:
        ident = json.loads((ROOT / "config" / "identity.json").read_text())
        portfolio = ident.get("company", {}).get("portfolio", {})
    except Exception as e:
        return f"Could not read identity.json: {e}"

    if not portfolio:
        return "identity.json has no company.portfolio block — nothing to seed."

    data = _load()
    existing_slugs = {p.get("slug") for p in data.get("projects", [])}
    added = 0
    for name, blurb in portfolio.items():
        slug = _slugify(name)
        if slug in existing_slugs:
            continue
        data["projects"].append({
            "slug": slug,
            "name": name,
            "type": "iOS app",
            "url": "",
            "client": None,
            "is_public": True,
            "tech": ["Swift", "SwiftUI"],
            "blurb": blurb,
            "highlights": [],
            "screenshots": [],
            "launched": "",
            "last_promoted": None,
            "promote_count": 0,
        })
        added += 1
    _save(data)
    return f"Seeded {added} projects from identity.json portfolio. Total now: {len(data['projects'])}."


# ---------- Public API ----------

def list_projects(public_only: bool = False) -> str:
    data = _load()
    projects = data.get("projects", [])
    if public_only:
        projects = [p for p in projects if p.get("is_public")]
    if not projects:
        return (
            "No projects in registry yet. Run bootstrap_from_identity() or "
            "add one with add_project(slug, name, blurb, ...)."
        )
    lines = [f"Registered projects ({len(projects)} total):"]
    for p in projects:
        flags = []
        if not p.get("is_public"):
            flags.append("PRIVATE")
        if p.get("client"):
            flags.append(f"client:{p['client']}")
        flag_str = f" [{', '.join(flags)}]" if flags else ""
        last = p.get("last_promoted") or "never"
        lines.append(
            f"- {p.get('name', '?')} ({p.get('slug', '?')}){flag_str}: "
            f"{p.get('blurb', '')[:100]}  | promoted {p.get('promote_count', 0)}x, last: {last}"
        )
    return "\n".join(lines)


def get_project(slug_or_name: str) -> dict | None:
    data = _load()
    needle = (slug_or_name or "").lower().strip()
    for p in data.get("projects", []):
        if p.get("slug", "").lower() == needle or p.get("name", "").lower() == needle:
            return p
    return None


def add_project(
    name: str,
    blurb: str,
    url: str = "",
    tech: list | None = None,
    client: str | None = None,
    is_public: bool = True,
    highlights: list | None = None,
    launched: str = "",
    type_: str = "iOS app",
) -> str:
    data = _load()
    slug = _slugify(name)
    if any(p.get("slug") == slug for p in data["projects"]):
        return f"Project with slug '{slug}' already exists. Use update_project to modify."
    data["projects"].append({
        "slug": slug,
        "name": name,
        "type": type_,
        "url": url,
        "client": client,
        "is_public": is_public,
        "tech": tech or [],
        "blurb": blurb,
        "highlights": highlights or [],
        "screenshots": [],
        "launched": launched,
        "last_promoted": None,
        "promote_count": 0,
    })
    _save(data)
    return f"Added project '{name}' (slug: {slug}). Registry now has {len(data['projects'])} projects."


def mark_promoted(slug: str) -> str:
    """Called by content_strategist after a project gets used in a draft."""
    data = _load()
    for p in data["projects"]:
        if p.get("slug") == slug:
            p["last_promoted"] = time.strftime("%Y-%m-%dT%H:%M:%S")
            p["promote_count"] = p.get("promote_count", 0) + 1
            _save(data)
            return f"Marked '{slug}' as promoted ({p['promote_count']}x total)."
    return f"No project with slug '{slug}' found."


def pick_next_to_promote() -> dict | None:
    """Pick the public project that hasn't been promoted in the longest time."""
    data = _load()
    public = [p for p in data.get("projects", []) if p.get("is_public")]
    if not public:
        return None
    public.sort(key=lambda p: p.get("last_promoted") or "")
    return public[0]
