"""
BLAI Agent — Gemini function-calling loop.

Difference vs brain.py:
  brain.py = keyword routing (your code decides which skill to run).
  agent.py = Gemini decides which tool to call, when to chain calls,
             when to stop, and what to say back. The model thinks.

Flow:
  user_msg
    -> Gemini (with tool list)
    -> Gemini emits a function_call
    -> we run the matching Python skill
    -> we feed the result back as function_response
    -> loop until Gemini emits plain text (final answer)

Reflection:
  Every run appends a JSON line to memory/agent_reflections.jsonl
  with {timestamp, user_msg, tools_used, final_answer}.
  The next run reads the last 5 reflections so the agent stays
  coherent across calls without retraining anything.
"""

import json
import time
import requests
from pathlib import Path

CONFIG_DIR = Path(__file__).parent.parent / "config"
MEMORY_DIR = Path(__file__).parent.parent / "memory"
REFLECTIONS = MEMORY_DIR / "agent_reflections.jsonl"

# Flash first — bigger free quota (1500 req/day/key). Pro as backup for hard
# reasoning. Both support function-calling identically.
GEMINI_MODELS = ["gemini-2.5-flash", "gemini-2.5-pro"]
MAX_ITERATIONS = 8


# ---------- API keys (reuse brain.py rotation) ----------
def _get_keys() -> list:
    f = CONFIG_DIR / "api_keys.json"
    if f.exists():
        return json.loads(f.read_text()).get("gemini", [])
    return []


# ---------- Tool catalog ----------
# Each entry: (gemini_declaration, python_executor)
# The declaration is what Gemini sees so it can decide whether to call it.
# The executor is what we run when Gemini does call it.

def _tool_hunt_leads(query: str = None, platforms: list = None) -> str:
    from skills.lead_hunter_real import hunt_leads
    return hunt_leads(query=query, platforms=platforms or ["reddit", "hackernews"])


def _tool_send_email(to: str, subject: str, body: str) -> str:
    from skills.email_outreach import send_outreach_email
    return send_outreach_email(to=to, subject=subject, body=body)


def _tool_post_social(platform: str, content: str, image_url: str = None, title: str = None) -> str:
    from skills.social_poster_real import post_to_social
    return post_to_social(platform=platform, content=content, image_url=image_url, title=title)


def _tool_market_snapshot() -> str:
    from skills.crypto_intel import get_market_snapshot
    snap = get_market_snapshot()
    return json.dumps(snap, default=str)[:4000]


def _tool_lead_stats() -> str:
    from skills.lead_hunter_real import get_lead_stats
    return get_lead_stats()


def _tool_outreach_stats() -> str:
    from skills.email_outreach import get_outreach_stats
    return get_outreach_stats()


def _tool_write_note(filename: str, content: str) -> str:
    notes_dir = MEMORY_DIR / "agent_notes"
    notes_dir.mkdir(parents=True, exist_ok=True)
    safe = filename.replace("/", "_").replace("..", "_")[:120]
    if not safe.endswith(".md"):
        safe += ".md"
    (notes_dir / safe).write_text(content)
    return f"saved {safe}"


TOOLS = {
    "hunt_leads": (
        {
            "name": "hunt_leads",
            "description": "Search Reddit and HackerNews for potential clients matching a niche. Returns a scored list of leads (title, url, score, where).",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search terms, e.g. 'looking for iOS dev' or 'need ai agent'"},
                    "platforms": {"type": "array", "items": {"type": "string"}, "description": "Optional. Subset of ['reddit','hackernews']"},
                },
                "required": ["query"],
            },
        },
        _tool_hunt_leads,
    ),
    "send_email": (
        {
            "name": "send_email",
            "description": "Send an outreach email from info@blacklayers.ca via Zoho SMTP. Use only after the user explicitly approves a draft, or when they directly ask for a send.",
            "parameters": {
                "type": "object",
                "properties": {
                    "to": {"type": "string"},
                    "subject": {"type": "string"},
                    "body": {"type": "string"},
                },
                "required": ["to", "subject", "body"],
            },
        },
        _tool_send_email,
    ),
    "post_social": (
        {
            "name": "post_social",
            "description": "Post content to a social platform via Make.com (twitter, linkedin, instagram, tiktok, facebook).",
            "parameters": {
                "type": "object",
                "properties": {
                    "platform": {"type": "string"},
                    "content": {"type": "string"},
                    "image_url": {"type": "string"},
                    "title": {"type": "string"},
                },
                "required": ["platform", "content"],
            },
        },
        _tool_post_social,
    ),
    "market_snapshot": (
        {
            "name": "market_snapshot",
            "description": "Get a live crypto market snapshot (BTC, ETH, dominance, fear & greed, funding). Use for any trading or market question.",
            "parameters": {"type": "object", "properties": {}},
        },
        _tool_market_snapshot,
    ),
    "lead_stats": (
        {
            "name": "lead_stats",
            "description": "Summary of all leads collected so far (total, by platform, top scoring).",
            "parameters": {"type": "object", "properties": {}},
        },
        _tool_lead_stats,
    ),
    "outreach_stats": (
        {
            "name": "outreach_stats",
            "description": "Summary of outreach emails sent so far.",
            "parameters": {"type": "object", "properties": {}},
        },
        _tool_outreach_stats,
    ),
    "write_note": (
        {
            "name": "write_note",
            "description": "Persist a short note (plan, observation, decision) to BLAI's agent memory so future runs can read it.",
            "parameters": {
                "type": "object",
                "properties": {
                    "filename": {"type": "string"},
                    "content": {"type": "string"},
                },
                "required": ["filename", "content"],
            },
        },
        _tool_write_note,
    ),
}


# ---------- Reflections (cheap "improvement over time") ----------
def _load_recent_reflections(n: int = 5) -> list:
    if not REFLECTIONS.exists():
        return []
    try:
        lines = REFLECTIONS.read_text().strip().splitlines()
        return [json.loads(l) for l in lines[-n:]]
    except Exception:
        return []


def _save_reflection(entry: dict):
    REFLECTIONS.parent.mkdir(parents=True, exist_ok=True)
    with REFLECTIONS.open("a") as f:
        f.write(json.dumps(entry) + "\n")


# ---------- System prompt (small, focused on tool use) ----------
SYSTEM = """You are BLAI, Abdul Hafeez's autonomous AI partner.

You THINK before you act. For every user request:
  1. Decide if a tool is needed. If yes, pick the right one and call it.
  2. Read the tool result. Decide whether to call another tool, or answer.
  3. Chain tools when the goal requires it (e.g. hunt_leads -> send_email).
  4. If the request is just a question, answer directly without tools.
  5. NEVER call send_email without an explicit go-ahead from the user OR a clear instruction to send a specific draft.

Be terse. Boss is technical. No fluff.

If you are unsure of a fact, say so. Do not invent.
"""


# ---------- Gemini call (function-calling format) ----------
def _gemini_call(contents: list) -> dict:
    """One round trip with tool list. Tries Flash on every key, then Pro on every key."""
    keys = _get_keys()
    if not keys:
        return {}

    payload = {
        "systemInstruction": {"parts": [{"text": SYSTEM}]},
        "contents": contents,
        "tools": [{"functionDeclarations": [decl for decl, _ in TOOLS.values()]}],
        "generationConfig": {"maxOutputTokens": 2048, "temperature": 0.4},
    }

    for model in GEMINI_MODELS:
        for key in keys:
            try:
                r = requests.post(
                    f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={key}",
                    json=payload,
                    timeout=45,
                )
                if r.status_code == 200:
                    cands = r.json().get("candidates", [])
                    if cands:
                        return cands[0]
            except Exception:
                continue
    return {}


# ---------- Main loop ----------
def run(user_message: str) -> str:
    """Run the thinking agent on a user message. Returns the final reply."""

    reflections = _load_recent_reflections()
    preamble = ""
    if reflections:
        last = reflections[-3:]
        preamble = "Recent prior runs (for continuity):\n" + "\n".join(
            f"- asked: {r.get('user_msg','')[:80]} | answered: {r.get('final_answer','')[:80]}"
            for r in last
        ) + "\n\n"

    contents = [{"role": "user", "parts": [{"text": preamble + user_message}]}]
    tools_used = []
    final_text = ""

    for _ in range(MAX_ITERATIONS):
        cand = _gemini_call(contents)
        if not cand:
            final_text = "Agent: Gemini call failed (no keys or all rate-limited)."
            break

        parts = (cand.get("content") or {}).get("parts", []) or []

        # Did Gemini ask to call a tool?
        fn_call = next((p.get("functionCall") for p in parts if p.get("functionCall")), None)
        if fn_call:
            name = fn_call.get("name")
            args = fn_call.get("args") or {}
            tools_used.append(name)

            decl, executor = TOOLS.get(name, (None, None))
            if not executor:
                tool_result = f"unknown tool: {name}"
            else:
                try:
                    tool_result = executor(**args)
                except TypeError:
                    # Some skills accept no args; retry without
                    try:
                        tool_result = executor()
                    except Exception as e:
                        tool_result = f"tool error: {e}"
                except Exception as e:
                    tool_result = f"tool error: {e}"

            # Append the model's call + our result, then loop
            contents.append({"role": "model", "parts": [{"functionCall": fn_call}]})
            contents.append({
                "role": "user",
                "parts": [{
                    "functionResponse": {
                        "name": name,
                        "response": {"content": str(tool_result)[:6000]},
                    }
                }],
            })
            continue

        # Otherwise this is the final answer
        final_text = next((p.get("text", "") for p in parts if p.get("text")), "").strip()
        break

    if not final_text:
        final_text = "Agent: hit iteration cap without a final answer."

    _save_reflection({
        "ts": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "user_msg": user_message,
        "tools_used": tools_used,
        "final_answer": final_text[:500],
    })

    return final_text


if __name__ == "__main__":
    import sys
    msg = " ".join(sys.argv[1:]) or "what does the market look like right now?"
    print(run(msg))
