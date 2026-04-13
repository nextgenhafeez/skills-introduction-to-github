"""
BLAI skill: GitHub Repository Browser (REAL, not a stub).

Gives the agent the ability to browse, read, and summarise any repo that
the configured GitHub token has access to. This is the missing piece that
lets BLAI answer questions about client projects on Boss's behalf.

Uses the GitHub REST API v3 (api.github.com) with the PAT from
config/api_keys.json under "github".

Public functions used by the skill router:
  - list_repos(owner=None)              -> str   (list all repos for owner)
  - get_repo_info(repo_full_name)       -> str   (repo summary: desc, lang, stars)
  - list_repo_files(repo_full_name, path="") -> str (file tree)
  - read_file(repo_full_name, path)     -> str   (raw file contents, up to 1MB)
  - search_repo(repo_full_name, query)  -> str   (code search within a repo)
  - get_readme(repo_full_name)          -> str   (README content)
  - summarise_project(repo_full_name)   -> str   (auto-generated project summary)

All network errors are caught and surfaced verbatim — never fabricated.
"""
from __future__ import annotations

import base64
import json
import time
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parent.parent
API_KEYS_FILE = ROOT / "config" / "api_keys.json"
CACHE_DIR = ROOT / "memory" / "github_cache"
CACHE_DIR.mkdir(parents=True, exist_ok=True)

CACHE_TTL = 10 * 60  # 10 min cache for repo data


def _load_token() -> str:
    """Load GitHub PAT from config."""
    try:
        config = json.loads(API_KEYS_FILE.read_text())
        return config.get("github", "")
    except Exception:
        return ""


def _load_owner() -> str:
    """Load default GitHub owner from config."""
    try:
        config = json.loads(API_KEYS_FILE.read_text())
        return config.get("github_owner", "nextgenhafeez")
    except Exception:
        return "nextgenhafeez"


def _headers() -> dict:
    token = _load_token()
    h = {
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "BLAI-Agent/2.0 (Black Layers)",
    }
    if token:
        h["Authorization"] = f"token {token}"
    return h


def _api_get(endpoint: str, params: dict = None) -> dict | list | None:
    """Make a GET request to the GitHub API."""
    url = f"https://api.github.com{endpoint}" if endpoint.startswith("/") else endpoint
    try:
        resp = requests.get(url, headers=_headers(), params=params, timeout=15)
        if resp.status_code == 200:
            return resp.json()
        elif resp.status_code == 404:
            return {"_error": f"Not found: {endpoint}. Check if the repo exists and the token has access."}
        elif resp.status_code == 401:
            return {"_error": "GitHub token is invalid or expired. Please update config/api_keys.json."}
        elif resp.status_code == 403:
            return {"_error": f"Access denied (403). The token may lack permissions, or rate limit hit. Headers: {dict(resp.headers).get('X-RateLimit-Remaining', '?')} remaining."}
        else:
            return {"_error": f"GitHub API returned {resp.status_code}: {resp.text[:300]}"}
    except Exception as e:
        return {"_error": f"Network error reaching GitHub API: {str(e)[:200]}"}


# ============================================================
# PUBLIC API
# ============================================================

def list_repos(owner: str = None) -> str:
    """
    List all repos visible to the token for a given owner.
    If owner is None, uses the default github_owner from config.
    """
    owner = owner or _load_owner()
    data = _api_get(f"/users/{owner}/repos", params={"per_page": 100, "sort": "updated"})

    if isinstance(data, dict) and "_error" in data:
        # Try as org instead
        data = _api_get(f"/orgs/{owner}/repos", params={"per_page": 100, "sort": "updated"})

    if isinstance(data, dict) and "_error" in data:
        return f"❌ {data['_error']}"

    if not isinstance(data, list) or len(data) == 0:
        return f"No repositories found for '{owner}'."

    lines = [f"📂 *Repositories for {owner}* ({len(data)} found):\n"]
    for repo in data[:50]:  # Cap at 50 to avoid massive messages
        name = repo.get("name", "?")
        desc = (repo.get("description") or "No description")[:80]
        private = "🔒" if repo.get("private") else "🌐"
        lang = repo.get("language") or "—"
        updated = (repo.get("updated_at") or "")[:10]
        lines.append(f"  {private} *{name}* ({lang}) — {desc} [updated: {updated}]")

    return "\n".join(lines)


def get_repo_info(repo_full_name: str) -> str:
    """Get summary info about a specific repo (e.g. 'nextgenhafeez/crm-investment-platform')."""
    if "/" not in repo_full_name:
        repo_full_name = f"{_load_owner()}/{repo_full_name}"

    data = _api_get(f"/repos/{repo_full_name}")

    if isinstance(data, dict) and "_error" in data:
        return f"❌ {data['_error']}"

    if not isinstance(data, dict):
        return "❌ Unexpected response from GitHub."

    lines = [
        f"📦 *{data.get('full_name', repo_full_name)}*",
        f"Description: {data.get('description') or 'None'}",
        f"Language: {data.get('language') or 'Not detected'}",
        f"Stars: {data.get('stargazers_count', 0)} | Forks: {data.get('forks_count', 0)}",
        f"Private: {'Yes' if data.get('private') else 'No'}",
        f"Default Branch: {data.get('default_branch', 'main')}",
        f"Created: {(data.get('created_at') or '')[:10]}",
        f"Last Push: {(data.get('pushed_at') or '')[:10]}",
        f"URL: {data.get('html_url', '')}",
    ]

    topics = data.get("topics", [])
    if topics:
        lines.append(f"Topics: {', '.join(topics)}")

    return "\n".join(lines)


def list_repo_files(repo_full_name: str, path: str = "") -> str:
    """List files and directories at a given path in a repo."""
    if "/" not in repo_full_name:
        repo_full_name = f"{_load_owner()}/{repo_full_name}"

    endpoint = f"/repos/{repo_full_name}/contents/{path}".rstrip("/")
    data = _api_get(endpoint)

    if isinstance(data, dict) and "_error" in data:
        return f"❌ {data['_error']}"

    if not isinstance(data, list):
        # Could be a single file
        if isinstance(data, dict) and data.get("type") == "file":
            return f"'{path}' is a file, not a directory. Use read_file() to see its contents."
        return "❌ Unexpected response. The path may not exist."

    lines = [f"📁 *{repo_full_name}/{path or '(root)'}* — {len(data)} items:\n"]
    # Sort: directories first, then files
    dirs = sorted([f for f in data if f.get("type") == "dir"], key=lambda x: x["name"])
    files = sorted([f for f in data if f.get("type") != "dir"], key=lambda x: x["name"])

    for d in dirs:
        lines.append(f"  📂 {d['name']}/")
    for f in files:
        size = f.get("size", 0)
        size_str = f"{size:,}B" if size < 10000 else f"{size/1024:.1f}KB"
        lines.append(f"  📄 {f['name']} ({size_str})")

    return "\n".join(lines)


def read_file(repo_full_name: str, path: str) -> str:
    """Read the contents of a specific file from a repo."""
    if "/" not in repo_full_name:
        repo_full_name = f"{_load_owner()}/{repo_full_name}"

    endpoint = f"/repos/{repo_full_name}/contents/{path}"
    data = _api_get(endpoint)

    if isinstance(data, dict) and "_error" in data:
        return f"❌ {data['_error']}"

    if not isinstance(data, dict):
        return "❌ Unexpected response."

    if data.get("type") != "file":
        return f"'{path}' is a {data.get('type', 'unknown')}, not a file."

    # Check size — GitHub API returns base64 for files up to 1MB
    size = data.get("size", 0)
    if size > 1_000_000:
        return f"⚠️ File is too large ({size/1024:.0f}KB). GitHub API only serves files up to 1MB via contents endpoint."

    content_b64 = data.get("content", "")
    encoding = data.get("encoding", "")

    if encoding == "base64" and content_b64:
        try:
            content = base64.b64decode(content_b64).decode("utf-8", errors="replace")
            # Truncate very long files for WhatsApp readability
            if len(content) > 4000:
                content = content[:4000] + f"\n\n... [TRUNCATED — full file is {len(content)} chars] ..."
            return f"📄 *{path}* ({size:,} bytes):\n```\n{content}\n```"
        except Exception as e:
            return f"❌ Failed to decode file content: {e}"
    else:
        return f"⚠️ File encoding is '{encoding}', not base64. Cannot decode."


def get_readme(repo_full_name: str) -> str:
    """Get the README file for a repo."""
    if "/" not in repo_full_name:
        repo_full_name = f"{_load_owner()}/{repo_full_name}"

    data = _api_get(f"/repos/{repo_full_name}/readme")

    if isinstance(data, dict) and "_error" in data:
        return f"❌ {data['_error']}"

    if not isinstance(data, dict):
        return "❌ Unexpected response."

    content_b64 = data.get("content", "")
    if content_b64:
        try:
            content = base64.b64decode(content_b64).decode("utf-8", errors="replace")
            if len(content) > 3000:
                content = content[:3000] + "\n\n... [TRUNCATED] ..."
            return f"📖 *README for {repo_full_name}:*\n\n{content}"
        except Exception as e:
            return f"❌ Decode error: {e}"

    return "No README found for this repo."


def search_repo(repo_full_name: str, query: str) -> str:
    """Search for code within a specific repo."""
    if "/" not in repo_full_name:
        repo_full_name = f"{_load_owner()}/{repo_full_name}"

    search_q = f"{query} repo:{repo_full_name}"
    data = _api_get("/search/code", params={"q": search_q, "per_page": 10})

    if isinstance(data, dict) and "_error" in data:
        return f"❌ {data['_error']}"

    if not isinstance(data, dict):
        return "❌ Unexpected response."

    total = data.get("total_count", 0)
    items = data.get("items", [])

    if total == 0:
        return f"No results for '{query}' in {repo_full_name}."

    lines = [f"🔍 *Search results for '{query}' in {repo_full_name}* ({total} hits):\n"]
    for item in items[:10]:
        name = item.get("name", "?")
        path = item.get("path", "?")
        lines.append(f"  📄 {path}")

    return "\n".join(lines)


def summarise_project(repo_full_name: str) -> str:
    """
    Auto-generate a project summary by reading repo info, README, and file structure.
    This is what BLAI uses to answer client questions intelligently.
    """
    if "/" not in repo_full_name:
        repo_full_name = f"{_load_owner()}/{repo_full_name}"

    parts = []

    # 1. Basic info
    info = get_repo_info(repo_full_name)
    parts.append(info)
    parts.append("")

    # 2. File structure (root only)
    files = list_repo_files(repo_full_name)
    parts.append(files)
    parts.append("")

    # 3. README
    readme = get_readme(repo_full_name)
    parts.append(readme)

    return "\n".join(parts)


def get_client_repos(client_name: str) -> str:
    """List repos associated with a specific client from config."""
    try:
        config = json.loads(API_KEYS_FILE.read_text())
        client_repos = config.get("client_repos", {})
        owner = config.get("github_owner", "nextgenhafeez")

        # Try exact match first, then fuzzy
        repos = client_repos.get(client_name.lower())
        if not repos:
            # Fuzzy match
            for key, value in client_repos.items():
                if client_name.lower() in key.lower() or key.lower() in client_name.lower():
                    repos = value
                    break

        if not repos:
            return f"No repos mapped for client '{client_name}'. Known clients: {', '.join(client_repos.keys())}"

        lines = [f"📂 *Repos for client '{client_name}':*"]
        for repo_name in repos:
            info = get_repo_info(f"{owner}/{repo_name}")
            lines.append(f"\n{info}")

        return "\n".join(lines)
    except Exception as e:
        return f"❌ Error loading client repos: {e}"


if __name__ == "__main__":
    # Quick test
    print(list_repos())
