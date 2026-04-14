#!/usr/bin/env python3
"""
Social Poster Real — Post to social platforms via Make.com webhooks.
Now Scenario-Aware: Checks Make.com API to see if scenarios are active/valid.
"""

import json
import time
import requests
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.brain import think_simple
from skills.make_com import (
    call_webhook, call_webhook_by_name, create_webhook,
    _load_webhooks, _get_webhooks_config
)

MEMORY_DIR = ROOT / "memory"
POSTS_LOG = MEMORY_DIR / "social_posts_log.json"
API_KEYS_FILE = ROOT / "config/api_keys.json"

def _load_config():
    if API_KEYS_FILE.exists():
        return json.loads(API_KEYS_FILE.read_text())
    return {}

def _check_make_scenario_status(scenario_id: str) -> dict:
    """Check if a Make.com scenario is actually turned ON and has no errors."""
    config = _load_config()
    make_config = config.get("make_com", {})
    if not isinstance(make_config, dict):
        return {"ok": False, "error": "Invalid make_com config"}

    api_token = make_config.get("api_token")
    base_url = make_config.get("base_url", "https://eu1.make.com/api/v2")
    
    if not api_token or not scenario_id:
        return {"ok": False, "error": "Missing Make.com API token or Scenario ID"}
    
    try:
        url = f"{base_url}/scenarios/{scenario_id}"
        headers = {"Authorization": f"Token {api_token}"}
        resp = requests.get(url, headers=headers, timeout=10)
        
        if resp.status_code == 200:
            data = resp.json().get("scenario", {})
            return {
                "ok": True,
                "active": data.get("isActive", False),
                "name": data.get("name", "Unknown"),
                "invalid": data.get("isinvalid", False),
                "last_run": data.get("last_run_at")
            }
        
        # Fallback: if single fetch is forbidden, try listing scenarios
        if resp.status_code == 403:
            list_url = f"{base_url}/scenarios"
            org_id = make_config.get("organization_id")
            params = {"organizationId": org_id} if org_id else {}
            list_resp = requests.get(list_url, headers=headers, params=params, timeout=15)
            if list_resp.status_code == 200:
                scenarios = list_resp.json().get("scenarios", [])
                for s in scenarios:
                    if str(s.get("id")) == str(scenario_id):
                        return {
                            "ok": True, 
                            "active": s.get("isActive", False),
                            "name": s.get("name", "Unknown"),
                            "invalid": s.get("isinvalid", False),
                            "last_run": s.get("lastEdit")
                        }
        
        return {"ok": False, "error": f"Make API status {resp.status_code}"}
    except Exception as e:
        return {"ok": False, "error": str(e)}

def _save_post_log(entry: dict):
    MEMORY_DIR.mkdir(parents=True, exist_ok=True)
    log = []
    if POSTS_LOG.exists():
        try:
            log = json.loads(POSTS_LOG.read_text())
        except:
            log = []
    log.append({**entry, "ts": int(time.time())})
    POSTS_LOG.write_text(json.dumps(log[-100:], indent=2))

def post_to_social(platform: str, content: str, image_url: str = None, title: str = None) -> str:
    """Post with scenario health check."""
    config = _load_config()
    make_config = config.get("make_com", {})
    if not isinstance(make_config, dict):
        return "❌ Invalid Make.com configuration."

    wh_config = make_config.get("webhooks", {})
    if not isinstance(wh_config, dict):
        return "❌ Missing webhooks configuration."
    
    # Find webhook for platform
    wh_data = None
    wh_key = None
    for k, v in wh_config.items():
        if not isinstance(v, dict): continue
        platforms = v.get("platforms", [])
        if platform.lower() in [str(p).lower() for p in platforms]:
            wh_data = v
            wh_key = k
            break
            
    if not wh_data:
        return f"❌ No webhook configured for platform: {platform}"
    
    wh_url = wh_data.get("url")
    scenario_id = wh_data.get("scenario_id")
    
    # 1. Check health if scenario ID exists
    health_info = ""
    if scenario_id:
        health = _check_make_scenario_status(scenario_id)
        if health["ok"]:
            if not health["active"]:
                return f"⚠️ Make.com Scenario '{health['name']}' is currently OFF. Please enable it to post to {platform}."
            if health["invalid"]:
                return f"❌ Make.com Scenario '{health['name']}' is INVALID (Check credentials)."
            health_info = f" (Scenario: {health['name']} is active)"
        else:
            health_info = f" (Health check skipped: {health['error']})"

    # 2. Trigger Webhook
    payload = {
        "platform": platform,
        "content": content,
        "text": content,  # Alias for Buffer/LinkedIn/FB expectation
        "title": title or (content[:50] + "..." if len(content) > 50 else content),
        "image_url": image_url,
        "media_url": image_url, # Alias for different media expectations
        "source": "BLAI-v2"
    }
    
    try:
        resp = requests.post(wh_url, json=payload, timeout=15)
        if resp.status_code == 200:
            _save_post_log({"platform": platform, "status": "success", "platform_key": wh_key})
            return f"✅ Successfully triggered {platform} post via {wh_key}{health_info}."
        else:
            _save_post_log({"platform": platform, "status": "failed", "code": resp.status_code})
            return f"❌ Make.com Webhook returned error {resp.status_code} for {platform}."
    except Exception as e:
        return f"❌ Failed to reach Make.com for {platform}: {str(e)}"

def post_to_all(contents: dict, image_url: str = None) -> str:
    """Post multiple contents to multiple platforms."""
    summaries = []
    for platform, text in contents.items():
        res = post_to_social(platform, text, image_url)
        summaries.append(res)
    return "\n".join(summaries)

def get_posting_stats() -> str:
    """Return health snapshot of all scenarios and recent posts."""
    config = _load_config()
    wh_config = config.get("make_com", {}).get("webhooks", {})
    
    lines = ["📊 *App Promotion & Social Health:*"]
    
    for k, v in wh_config.items():
        sid = v.get("scenario_id")
        platforms = ", ".join(v.get("platforms", []))
        if sid:
            h = _check_make_scenario_status(sid)
            status = "🟢 ACTIVE" if (h["ok"] and h["active"] and not h["invalid"]) else "🔴 INACTIVE/ERROR"
            if h.get("invalid"): status = "🟡 INVALID CREDENTIALS"
            lines.append(f"- {platforms}: {status} (ID: {sid})")
        else:
            lines.append(f"- {platforms}: ⚪ NO SCENARIO ID (Manual Webhook Only)")
            
    return "\n".join(lines)

if __name__ == "__main__":
    print(get_posting_stats())
