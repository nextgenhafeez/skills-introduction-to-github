import json, time, re
from pathlib import Path

_BASE = Path(__file__).parent.parent
MOOD_FILE = _BASE / "memory" / "mood_history.json"
MOOD_TAG_RE = re.compile(r"\[MOOD:\s*([a-zA-Z]+)\s*\]", re.IGNORECASE)

def parse_and_strip_mood(reply: str):
    if not reply:
        return reply, None
    matches = list(MOOD_TAG_RE.finditer(reply))
    if not matches:
        return reply, None
    mood = matches[-1].group(1).lower()
    clean_reply = MOOD_TAG_RE.sub("", reply).strip()
    return clean_reply, mood

def save_mood(phone: str, mood: str, message: str):
    if not mood:
        return
    try:
        MOOD_FILE.parent.mkdir(parents=True, exist_ok=True)
        try:
            data = json.loads(MOOD_FILE.read_text())
        except Exception:
            data = []
        data.append({
            "ts": int(time.time()),
            "phone": phone,
            "mood": mood,
            "excerpt": (message or "")[:80],
        })
        data = data[-20:]
        MOOD_FILE.write_text(json.dumps(data, indent=2))
    except Exception:
        pass

def get_mood_context(phone: str) -> str:
    try:
        data = json.loads(MOOD_FILE.read_text())
    except Exception:
        return ""
    boss_moods = [d for d in data if d.get("phone") == phone][-6:]
    if not boss_moods:
        return ""
    trail = " -> ".join(d["mood"] for d in boss_moods)
    last_ts = boss_moods[-1]["ts"]
    mins_ago = max(0, int((time.time() - last_ts) / 60))
    return ("\n\nBOSS RECENT MOOD TREND (oldest -> newest): " + trail +
            ". Last reading " + str(mins_ago) + " min ago. Adapt your response style accordingly.")

def finalize_reply(save_conv, phone: str, reply: str, message: str, is_boss_msg: bool) -> str:
    clean, mood = parse_and_strip_mood(reply)
    
    # HARD OVERRIDE: Prevent LLM format hallucination from reaching WhatsApp
    clean = re.sub(r'\[READ\].*?\[/READ\]', '', clean, flags=re.DOTALL | re.IGNORECASE).strip()
    clean = re.sub(r'\[FILE\].*?\[/FILE\]', '', clean, flags=re.DOTALL | re.IGNORECASE).strip()
    clean = re.sub(r'\[EXEC\].*?\[/EXEC\]', '', clean, flags=re.DOTALL | re.IGNORECASE).strip()

    if is_boss_msg and mood:
        save_mood(phone, mood, message)
    save_conv(phone, "assistant", clean)
    return clean
