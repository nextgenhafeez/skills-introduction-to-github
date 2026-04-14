#!/usr/bin/env python3
"""
Make.com API Client — Manage scenarios, webhooks, and trigger automations.
Uses Make.com REST API v2 (eu1 region).
"""

import json
import time
import requests
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from pathlib import Path

CONFIG_DIR = Path(__file__).parent.parent / "config"
MEMORY_DIR = Path(__file__).parent.parent / "memory"
WEBHOOKS_FILE = MEMORY_DIR / "make_webhooks.json"


def _load_make_config() -> dict:
    """Load Make.com config from api_keys.json."""
    keys_file = CONFIG_DIR / "api_keys.json"
    if keys_file.exists():
        data = json.loads(keys_file.read_text())
        return data.get("make_com", {})
    return {}


def _headers() -> dict:
    """Auth headers for Make.com API."""
    config = _load_make_config()
    token = config.get("api_token", "")
    return {
        "Authorization": f"Token {token}",
        "Content-Type": "application/json"
    }


def _base_url() -> str:
    config = _load_make_config()
    return config.get("base_url", "https://eu1.make.com/api/v2")


def _get_webhooks_config() -> dict:
    """Get preconfigured webhook URLs."""
    config = _load_make_config()
    return config.get("webhooks", {})


def _save_webhook(name: str, url: str, purpose: str):
    """Save a webhook to local tracking file."""
    MEMORY_DIR.mkdir(parents=True, exist_ok=True)
    webhooks = {}
    if WEBHOOKS_FILE.exists():
        webhooks = json.loads(WEBHOOKS_FILE.read_text())

    webhooks[name] = {
        "url": url,
        "purpose": purpose,
        "created": time.strftime("%Y-%m-%dT%H:%M:%S")
    }
    WEBHOOKS_FILE.write_text(json.dumps(webhooks, indent=2))


def _load_webhooks() -> dict:
    """Load all saved webhooks."""
    if WEBHOOKS_FILE.exists():
        return json.loads(WEBHOOKS_FILE.read_text())
    return {}


# --- Public API functions (return WhatsApp-friendly strings) ---


def _org_id():
    return _load_make_config().get("organization_id")

def _team_id():
    return _load_make_config().get("team_id")

def _make_get(path, params=None):
    """GET helper that auto-injects organizationId."""
    p = dict(params or {})
    if "organizationId" not in p and _org_id():
        p["organizationId"] = _org_id()
    return requests.get(_base_url() + path, headers=_headers(), params=p, timeout=20)

def _make_post(path, payload=None, params=None):
    p = dict(params or {})
    if "organizationId" not in p and _org_id():
        p["organizationId"] = _org_id()
    return requests.post(_base_url() + path, headers=_headers(), params=p, json=payload or {}, timeout=30)

def _fetch_scenarios_raw():
    """Returns list of scenario dicts or empty list on failure."""
    try:
        r = _make_get("/scenarios")
        if r.status_code == 200:
            return r.json().get("scenarios", [])
    except Exception:
        pass
    return []


def health_snapshot() -> dict:
    """Structured snapshot for monitoring + alerting. Used by brain.py."""
    scenarios = _fetch_scenarios_raw()
    snap = {
        "ok": True,
        "total": len(scenarios),
        "active": 0,
        "inactive": 0,
        "invalid": 0,
        "scenarios": [],
        "errors": [],
    }
    if not scenarios:
        snap["ok"] = False
        snap["errors"].append("Cannot reach Make.com API or no scenarios returned")
        return snap
    for s in scenarios:
        is_active = bool(s.get("isActive"))
        is_invalid = bool(s.get("isinvalid"))
        if is_active:
            snap["active"] += 1
        else:
            snap["inactive"] += 1
        if is_invalid:
            snap["invalid"] += 1
        snap["scenarios"].append({
            "id": s.get("id"),
            "name": s.get("name"),
            "active": is_active,
            "invalid": is_invalid,
            "modules": [m.get("moduleName") for m in s.get("usedModules", [])],
            "packages": s.get("usedPackages", []),
            "ops": s.get("operations"),
            "last_edit": s.get("lastEdit"),
        })
    return snap


def monitor() -> str:
    """Human-readable health report for WhatsApp."""
    snap = health_snapshot()
    if not snap["ok"]:
        return "Make.com: API unreachable. " + ("; ".join(snap["errors"]) if snap["errors"] else "")
    lines = []
    lines.append("MAKE.COM HEALTH (" + str(snap["total"]) + " scenarios):")
    lines.append("  Active: " + str(snap["active"]) + "  |  Inactive: " + str(snap["inactive"]) + "  |  Invalid: " + str(snap["invalid"]))
    lines.append("")
    for s in snap["scenarios"]:
        flags = []
        flags.append("ON" if s["active"] else "OFF")
        if s["invalid"]:
            flags.append("INVALID")
        lines.append("  [" + "/".join(flags) + "] " + (s["name"] or "?") + " (id " + str(s["id"]) + ")")
        if s["packages"]:
            lines.append("       packages: " + ", ".join(s["packages"]))
    if snap["invalid"] > 0 or snap["inactive"] == snap["total"]:
        lines.append("")
        lines.append("ALERT: " + str(snap["invalid"]) + " invalid, " + str(snap["inactive"]) + " inactive. Open https://eu1.make.com/scenarios to fix.")
    return "\n".join(lines)


def find_scenario(query: str) -> dict:
    """Fuzzy find a scenario by partial name match."""
    q = (query or "").lower().strip()
    if not q:
        return {}
    for s in _fetch_scenarios_raw():
        name = (s.get("name") or "").lower()
        if q in name or any(q in (m.get("moduleName") or "").lower() for m in s.get("usedModules", [])):
            return s
    return {}


def status_of(query: str) -> str:
    """Get human-readable status of a scenario by name fragment."""
    s = find_scenario(query)
    if not s:
        return "No scenario matches '" + query + "'."
    parts = []
    parts.append("Scenario: " + (s.get("name") or "?"))
    parts.append("  ID: " + str(s.get("id")))
    parts.append("  Active: " + str(s.get("isActive")))
    parts.append("  Invalid: " + str(s.get("isinvalid")))
    parts.append("  Packages: " + ", ".join(s.get("usedPackages", [])))
    parts.append("  Modules: " + ", ".join(m.get("moduleName") for m in s.get("usedModules", [])))
    parts.append("  Operations used: " + str(s.get("operations")))
    parts.append("  Last edit: " + str(s.get("lastEdit")))
    if s.get("isinvalid"):
        parts.append("")
        parts.append("This scenario is INVALID. Open https://eu1.make.com/scenario/" + str(s.get("id")) + " to fix it.")
    elif not s.get("isActive"):
        parts.append("")
        parts.append("This scenario is OFF. Toggle it on at https://eu1.make.com/scenario/" + str(s.get("id")))
    return "\n".join(parts)

# ---------- /new helpers ----------


def list_scenarios() -> str:
    """List all Make.com scenarios in the account."""
    try:
        resp = _make_get("/scenarios", {"pg[limit]": 20})
        if resp.status_code == 200:
            data = resp.json()
            scenarios = data.get("scenarios", [])
            if not scenarios:
                return "No scenarios found in your Make.com account."

            lines = [f"MAKE.COM SCENARIOS ({len(scenarios)}):\n"]
            for s in scenarios:
                status = "ON" if s.get("isActive") else "OFF"
                name = s.get("name", "Unnamed")
                sid = s.get("id", "?")
                lines.append(f"  [{status}] {name} (ID: {sid})")
            return "\n".join(lines)

        elif resp.status_code == 401:
            return "Make.com API auth failed. Check api_token in config."
        else:
            return f"Make.com API error: {resp.status_code}"

    except Exception as e:
        return f"Failed to reach Make.com: {e}"


def run_scenario(scenario_id: int) -> str:
    """Trigger a Make.com scenario to run immediately."""
    try:
        resp = requests.post(
            f"{_base_url()}/scenarios/{scenario_id}/run",
            headers=_headers(),
            json={},
            timeout=30
        )
        if resp.status_code == 200:
            return f"Scenario {scenario_id} triggered successfully."
        elif resp.status_code == 401:
            return "Make.com auth failed."
        elif resp.status_code == 404:
            return f"Scenario {scenario_id} not found."
        else:
            detail = resp.text[:200] if resp.text else str(resp.status_code)
            return f"Failed to run scenario {scenario_id}: {detail}"

    except Exception as e:
        return f"Error triggering scenario: {e}"


def create_webhook(name: str, purpose: str = "") -> str:
    """
    Create a new custom webhook in Make.com.
    Note: The webhook still needs to be connected to a scenario in the Make.com UI.
    """
    try:
        resp = requests.post(
            f"{_base_url()}/hooks",
            headers=_headers(),
            json={"name": name, "typeName": "gateway-webhook"},
            timeout=15
        )
        if resp.status_code in (200, 201):
            hook = resp.json().get("hook", resp.json())
            hook_url = hook.get("url", "")
            hook_id = hook.get("id", "?")

            if hook_url:
                _save_webhook(name, hook_url, purpose)
                return (
                    f"Webhook created: {name}\n"
                    f"ID: {hook_id}\n"
                    f"URL: {hook_url}\n\n"
                    f"Next step: Go to Make.com and connect this webhook to a scenario."
                )
            else:
                return f"Webhook created (ID: {hook_id}) but no URL returned. Check Make.com dashboard."

        elif resp.status_code == 401:
            return "Make.com auth failed. Check API token."
        else:
            detail = resp.text[:200] if resp.text else str(resp.status_code)
            return f"Failed to create webhook: {detail}"

    except Exception as e:
        return f"Error creating webhook: {e}"


def call_webhook(webhook_url: str, data: dict) -> str:
    """Send data to a Make.com webhook URL to trigger a scenario."""
    try:
        resp = requests.post(
            webhook_url,
            json=data,
            timeout=15
        )
        if resp.status_code == 200:
            return "Webhook called successfully. Scenario should be running."
        else:
            return f"Webhook returned {resp.status_code}. It may not be connected to a scenario yet."

    except Exception as e:
        return f"Error calling webhook: {e}"


def call_webhook_by_name(name: str, data: dict) -> str:
    """Call a saved webhook by its name."""
    webhooks = _load_webhooks()
    # Also check preconfigured webhooks
    config_webhooks = _get_webhooks_config()

    url = None
    if name in webhooks:
        url = webhooks[name]["url"]
    elif name in config_webhooks:
        url = config_webhooks[name]

    if not url:
        available = list(webhooks.keys()) + list(config_webhooks.keys())
        return f"No webhook named '{name}'. Available: {', '.join(available) or 'none'}"

    return call_webhook(url, data)


def list_webhooks() -> str:
    """List all known webhooks (saved + preconfigured)."""
    saved = _load_webhooks()
    config_wh = _get_webhooks_config()

    lines = ["WEBHOOKS:\n"]

    if config_wh:
        lines.append("Preconfigured (from config):")
        for name, url in config_wh.items():
            short_url = url[:60] + "..." if len(url) > 60 else url
            lines.append(f"  {name}: {short_url}")

    if saved:
        lines.append("\nCreated by BLAI:")
        for name, info in saved.items():
            lines.append(f"  {name}: {info.get('purpose', 'no description')}")
            lines.append(f"    URL: {info['url'][:60]}...")

    if not saved and not config_wh:
        return "No webhooks configured yet."

    return "\n".join(lines)


def list_connections() -> str:
    """List Make.com connections (app integrations)."""
    try:
        resp = requests.get(
            f"{_base_url()}/connections",
            headers=_headers(),
            params={"pg[limit]": 20},
            timeout=15
        )
        if resp.status_code == 200:
            data = resp.json()
            connections = data.get("connections", [])
            if not connections:
                return "No connections found. Set up app connections in Make.com first."

            lines = [f"MAKE.COM CONNECTIONS ({len(connections)}):\n"]
            for c in connections:
                name = c.get("name", "Unnamed")
                app = c.get("accountType", "unknown")
                lines.append(f"  {name} ({app})")
            return "\n".join(lines)

        elif resp.status_code == 401:
            return "Make.com auth failed."
        else:
            return f"Make.com API error: {resp.status_code}"

    except Exception as e:
        return f"Failed to list connections: {e}"


def status() -> str:
    """Quick Make.com status check — can we connect?"""
    try:
        resp = requests.get(
            f"{_base_url()}/scenarios",
            headers=_headers(),
            params={"pg[limit]": 1},
            timeout=10
        )
        if resp.status_code == 200:
            count = len(resp.json().get("scenarios", []))
            webhooks = _load_webhooks()
            config_wh = _get_webhooks_config()
            return (
                f"Make.com: CONNECTED\n"
                f"Scenarios: accessible\n"
                f"Webhooks saved: {len(webhooks)}\n"
                f"Webhooks preconfigured: {len(config_wh)}"
            )
        elif resp.status_code == 401:
            return "Make.com: AUTH FAILED — check API token"
        else:
            return f"Make.com: ERROR {resp.status_code}"
    except Exception as e:
        return f"Make.com: UNREACHABLE — {e}"


if __name__ == "__main__":
    print(status())
    print()
    print(list_scenarios())
    print()
    print(list_webhooks())
