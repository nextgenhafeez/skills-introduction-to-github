"""
BLAI Brain — Direct Gemini API calls with minimal overhead.
~1,500 tokens system prompt vs OpenClaw's 44,000.
"""

import os
import json
import time
import requests
from pathlib import Path

CONFIG_DIR = Path(__file__).parent.parent / "config"
MEMORY_DIR = Path(__file__).parent.parent / "memory"

# Load system prompt and knowledge once
SYSTEM_PROMPT = (CONFIG_DIR / "system_prompt.txt").read_text()
IDENTITY = json.loads((CONFIG_DIR / "identity.json").read_text())
KNOWLEDGE = json.loads((CONFIG_DIR / "knowledge.json").read_text())

# Skill router for on-demand skill loading + real skill execution
from src.skill_router import find_relevant_skills, find_real_skill, execute_real_skill
from src.mood import parse_and_strip_mood, save_mood, get_mood_context, finalize_reply as _finalize_with_mood


def get_api_keys():
    """Load all Gemini API keys for rotation."""
    keys_file = CONFIG_DIR / "api_keys.json"
    if keys_file.exists():
        data = json.loads(keys_file.read_text())
        return data.get("gemini", [])
    key = os.environ.get("GOOGLE_API_KEY", os.environ.get("GEMINI_API_KEY", ""))
    return [key] if key else []


def get_groq_keys():
    """Load all Groq API keys for rotation (fallback when Gemini is exhausted)."""
    keys_file = CONFIG_DIR / "api_keys.json"
    if keys_file.exists():
        data = json.loads(keys_file.read_text())
        groq = data.get("groq", [])
        if isinstance(groq, str):
            return [groq] if groq else []
        return groq
    key = os.environ.get("GROQ_API_KEY", "")
    return [key] if key else []


# ---------- Provider state (smart switching) ----------
# Tracks which provider is currently active so we don't hammer dead keys on
# every request. When Gemini is exhausted we switch to Groq until a retry
# window passes, then probe Gemini again to see if the quota has reset.

STATE_FILE = MEMORY_DIR / "brain_state.json"
GEMINI_RETRY_SECONDS = 30 * 60  # probe Gemini every 30 min while on Groq


def get_brain_state() -> dict:
    """Load provider state. Defaults to gemini active."""
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text())
        except Exception:
            pass
    return {"active_provider": "gemini", "gemini_exhausted_at": 0, "groq_exhausted_at": 0}


def save_brain_state(state: dict):
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(state, indent=2))


def mark_provider(name: str):
    """Mark a provider as currently active (called on successful reply)."""
    state = get_brain_state()
    if state.get("active_provider") != name:
        state["active_provider"] = name
        save_brain_state(state)


def mark_exhausted(name: str):
    """Mark a provider as exhausted right now."""
    state = get_brain_state()
    state[f"{name}_exhausted_at"] = int(time.time())
    if name == "gemini":
        state["active_provider"] = "groq"
    save_brain_state(state)


def should_probe_gemini(state: dict) -> bool:
    """While on Groq, retry Gemini periodically in case quota reset."""
    last = state.get("gemini_exhausted_at", 0)
    return (time.time() - last) > GEMINI_RETRY_SECONDS


def _call_gemini(system_text: str, contents: list) -> str:
    """Try each Gemini key once. Returns reply text or '' on total failure."""
    keys = get_api_keys()
    if not keys:
        return ""
    all_429 = True
    for key in keys:
        try:
            resp = requests.post(
                f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-lite:generateContent?key={key}",
                json={
                    "systemInstruction": {"parts": [{"text": system_text}]},
                    "contents": contents,
                    "generationConfig": {"maxOutputTokens": 2048, "temperature": 0.7},
                },
                timeout=30,
            )
            if resp.status_code == 200:
                return resp.json()["candidates"][0]["content"]["parts"][0]["text"]
            if resp.status_code != 429:
                all_429 = False
        except Exception:
            all_429 = False
            continue
    # Only mark exhausted if every key returned 429 (real quota wall)
    if all_429:
        mark_exhausted("gemini")
    return ""


def _call_groq(system_text: str, history: list, message: str) -> str:
    """Try each Groq key once. Returns reply text or '' on total failure."""
    keys = get_groq_keys()
    if not keys:
        return ""
    groq_messages = [{"role": "system", "content": system_text}]
    for msg in history:
        role = "user" if msg["role"] == "user" else "assistant"
        groq_messages.append({"role": role, "content": msg["content"]})
    groq_messages.append({"role": "user", "content": message})

    # Cascade: try every key against 70b (full payload), then every key
    # against 8b-instant (TRIMMED payload because Groq free tier has a hard
    # 6000 TPM per-request ceiling on 8b which the full prompt blows past).
    # 70b first because it's higher quality; 8b only as a fallback.
    all_429 = True

    # Pass 1: 70b across all keys with full payload
    for groq_key in keys:
        try:
            resp = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={"Authorization": f"Bearer {groq_key}", "Content-Type": "application/json"},
                json={
                    "model": "llama-3.3-70b-versatile",
                    "messages": groq_messages,
                    "max_tokens": 2048,
                    "temperature": 0.7,
                },
                timeout=30,
            )
            if resp.status_code == 200:
                return resp.json()["choices"][0]["message"]["content"]
            if resp.status_code not in (429, 413):
                all_429 = False
        except Exception:
            all_429 = False
            continue

    # Pass 2: 8b-instant with TRIMMED payload (no history, short system text)
    # Why: 8b free tier rejects any request > 6000 tokens TOTAL (input+output).
    # Strip the system text down to its first 4500 chars (~1100 tokens) and
    # drop conversation history entirely. Then cap output at 800 tokens.
    # 1100 sys + 200 user + 800 output = ~2100 tokens, well under 6000.
    short_system = groq_messages[0]["content"]
    if len(short_system) > 4500:
        short_system = short_system[:4500] + "\n[...truncated for 8b cascade...]"
    user_msg = groq_messages[-1]["content"][:1500]
    short_messages = [
        {"role": "system", "content": short_system},
        {"role": "user", "content": user_msg},
    ]
    for groq_key in keys:
        try:
            resp = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={"Authorization": f"Bearer {groq_key}", "Content-Type": "application/json"},
                json={
                    "model": "llama-3.1-8b-instant",
                    "messages": short_messages,
                    "max_tokens": 800,
                    "temperature": 0.7,
                },
                timeout=30,
            )
            if resp.status_code == 200:
                return resp.json()["choices"][0]["message"]["content"]
            if resp.status_code not in (429, 413):
                all_429 = False
        except Exception:
            all_429 = False
            continue

    if all_429:
        mark_exhausted("groq")
    return ""


def get_conversation_memory(phone: str, limit: int = 10) -> list:
    """Load recent conversation history for a user."""
    conv_file = MEMORY_DIR / "conversations" / f"{phone}.json"
    if conv_file.exists():
        convs = json.loads(conv_file.read_text())
        return convs[-limit:]  # Last N messages
    return []


def save_conversation(phone: str, role: str, content: str):
    """Save a message to conversation history."""
    conv_dir = MEMORY_DIR / "conversations"
    conv_dir.mkdir(parents=True, exist_ok=True)
    conv_file = conv_dir / f"{phone}.json"

    convs = []
    if conv_file.exists():
        convs = json.loads(conv_file.read_text())

    convs.append({
        "role": role,
        "content": content,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S")
    })

    # Keep last 50 messages per user (rolling window)
    convs = convs[-50:]
    conv_file.write_text(json.dumps(convs, indent=2))


def get_context_for_user(phone: str) -> str:
    """Build minimal context string for a user."""
    user_info = IDENTITY.get("whatsappUsers", {}).get(phone, {})
    name = user_info.get("name", "Unknown")
    role = user_info.get("role", "unknown")

    # Load preferences/corrections
    prefs_file = MEMORY_DIR / "preferences.json"
    prefs = ""
    if prefs_file.exists():
        prefs_data = json.loads(prefs_file.read_text())
        if prefs_data:
            corrs = prefs_data.get("corrections", [])[-10:]
            prefs = "\nBoss corrections/preferences:\n" + "\n".join(
                f"- {p[:180]}" for p in corrs
            )

    # Load today's scorecard context
    today = time.strftime("%Y-%m-%d")
    daily_file = MEMORY_DIR / "daily" / f"{today}.json"
    daily_context = ""
    if daily_file.exists():
        daily = json.loads(daily_file.read_text())
        daily_context = f"\nToday so far: {daily.get('posts_created', 0)} posts, {daily.get('leads_found', 0)} leads, {daily.get('emails_sent', 0)} emails sent."

    # Load relevant knowledge sections
    knowledge_summary = ""
    lessons = KNOWLEDGE.get("agent_memory", {}).get("lessons_learned", [])[-5:]
    corrections = KNOWLEDGE.get("agent_memory", {}).get("corrections_from_boss", [])
    if lessons:
        knowledge_summary += "\nRecent lessons: " + "; ".join(lessons[-3:])
    if corrections:
        knowledge_summary += "\nBoss corrections: " + "; ".join(corrections[-3:])

    return f"Speaking with: {name} ({role}, {phone}){prefs}{daily_context}{knowledge_summary}"



# ---------- Self-improvement: correction detection + persistence ----------
# When Boss corrects BLAI ("no", "wrong", "don't", "actually", "never",
# "always", "remember"), the message is saved to preferences.json so it
# becomes a permanent rule loaded into every future conversation context.
# This is how BLAI gets smarter over time without manual prompt editing.

CORRECTION_SIGNALS = [
    "no ", "wrong", "don't", "do not", "stop ", "actually", "instead",
    "never ", "always ", "remember", "important", "correction", "fix this",
]
BOSS_PHONES = {"212641503230", "72426671055054"}


def is_boss(phone: str) -> bool:
    return phone in BOSS_PHONES


def looks_like_correction(message: str) -> bool:
    m = (message or "").lower().strip()
    if len(m) < 4:
        return False
    return any(sig in m for sig in CORRECTION_SIGNALS)


def save_boss_correction(text: str):
    """Append a Boss correction to preferences.json (deduped, capped)."""
    text = (text or "").strip()
    if not text:
        return
    f = MEMORY_DIR / "preferences.json"
    data = {"corrections": []}
    if f.exists():
        try:
            data = json.loads(f.read_text())
        except Exception:
            pass
    corrections = data.get("corrections", [])
    if text in corrections:
        return  # already learned this one
    corrections.append(text)
    data["corrections"] = corrections[-50:]  # rolling window of 50 lessons
    data["updated_at"] = time.strftime("%Y-%m-%dT%H:%M:%S")
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text(json.dumps(data, indent=2))


# ---------- Self-introspection: real runtime state on demand ----------
# When Boss asks technical questions about BLAI itself ("which model",
# "what api key", "your status", "diagnose yourself"), inject the REAL
# state into context so BLAI answers from facts, not from the prompt.

INTROSPECTION_SIGNALS = [
    "which model", "what model", "which ai", "what ai",
    "which api", "what api", "which key", "which provider",
    "your status", "are you using", "are you running",
    "diagnose yourself", "self status", "brain status",
    "groq or gemini", "gemini or groq",
]


def looks_like_introspection(message: str) -> bool:
    m = (message or "").lower()
    return any(sig in m for sig in INTROSPECTION_SIGNALS)


def get_self_status() -> str:
    """Return BLAI's real runtime state. Source of truth for self-questions."""
    state = get_brain_state()
    gemini_keys = get_api_keys()
    groq_keys = get_groq_keys()
    active = state.get("active_provider", "unknown")
    gem_exh = state.get("gemini_exhausted_at", 0)
    groq_exh = state.get("groq_exhausted_at", 0)

    def fmt(ts):
        if not ts:
            return "never"
        return time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime(ts))

    lines = [
        "",
        "[REAL-TIME SELF STATUS - answer Boss questions about model/keys/state from THIS, not from memory]",
        "- Active provider RIGHT NOW: " + active,
        "- Gemini: " + str(len(gemini_keys)) + " keys loaded, model gemini-2.5-flash-lite, last exhausted: " + fmt(gem_exh),
        "- Groq: " + str(len(groq_keys)) + " keys loaded, cascade llama-3.3-70b-versatile -> llama-3.1-8b-instant, last exhausted: " + fmt(groq_exh),
        "- This very reply you are generating now is being served by: " + active,
        "- State file: memory/brain_state.json",
        "- Switching rule: try Gemini first; on quota fall back to Groq; probe Gemini every 30 min while on Groq to detect quota reset; switch back automatically.",
    ]
    return "\n\n" + "\n".join(lines)




# ---------- Real URL verification (anti-hallucination tool) ----------
# Boss asked BLAI about a URL and BLAI invented a fake "GitHub Pages is
# disabled" diagnosis without running any command. To prevent that, when a
# message contains a URL, brain.py runs a real HTTP HEAD via curl and injects
# the actual status code into the prompt as ground truth.
import re
import subprocess as _subprocess

URL_REGEX = re.compile(r"https?://[^\s)>\]'\"]+")


def extract_urls(message: str) -> list:
    if not message:
        return []
    return URL_REGEX.findall(message)[:3]  # cap at 3 to keep prompt small


def url_check(url: str) -> str:
    """Run a real HTTP HEAD with curl. Returns a status string for context."""
    try:
        result = _subprocess.run(
            [
                "curl", "-sS", "-o", "/dev/null", "-L",
                "-w", "HTTP %{http_code} | final=%{url_effective} | size=%{size_download}",
                "--max-time", "8",
                url,
            ],
            capture_output=True, text=True, timeout=10,
        )
        return result.stdout.strip() or ("ERROR: " + result.stderr.strip()[:200])
    except Exception as e:
        return "ERROR: " + str(e)[:200]


def get_url_check_context(message: str) -> str:
    urls = extract_urls(message)
    if not urls:
        return ""
    lines = ["", "[REAL URL CHECK RESULTS - cite these as ground truth, do not invent anything else]"]
    for u in urls:
        lines.append("- " + u)
        lines.append("  " + url_check(u))
    return "\n".join(lines)




# ---------- Real lead data injection (anti-hallucination for leads) ----------
# When Boss or anyone asks about leads, inject the ACTUAL lead database stats
# into the prompt so BLAI cannot fabricate fictional Reddit/Twitter prospects.

LEAD_SIGNALS = [
    "lead", "leads", "prospect", "prospects", "pipeline",
    "update me about lead", "new lead", "any lead", "hunt lead", "find lead",
]


def looks_like_lead_question(message: str) -> bool:
    m = (message or "").lower()
    return any(sig in m for sig in LEAD_SIGNALS)


def get_real_lead_context() -> str:
    """Return REAL lead data from memory/leads.json — not a guess."""
    leads_file = MEMORY_DIR / "leads.json"
    if not leads_file.exists():
        return (
            "\n\n[REAL LEAD DATABASE - ground truth, do not fabricate anything beyond this]\n"
            "- leads.json does not exist yet. Total leads: 0.\n"
            "- If Boss asks, say: 'No leads in database yet. The lead hunter has not produced any results.'\n"
        )
    try:
        data = json.loads(leads_file.read_text())
    except Exception as e:
        return f"\n\n[REAL LEAD DATABASE ERROR: {e} — tell Boss the file is unreadable]\n"

    leads = data.get("leads", [])
    last_scan = data.get("last_scan", "never")
    total = len(leads)

    lines = [
        "",
        "[REAL LEAD DATABASE - ground truth from memory/leads.json, do not fabricate anything beyond this]\nOVERRIDE: If anything in the prior conversation history mentions specific leads, prospects, or platforms (Reddit, Twitter, Product Hunt) that are not in the structured data below, those past mentions were FABRICATED in earlier turns. Trust ONLY the data below.",
        f"- Total leads in database: {total}",
        f"- Last hunter scan: {last_scan}",
    ]
    if total == 0:
        lines.append("- CRITICAL: there are ZERO leads. If Boss asks about leads, say exactly: 'No leads in database yet. Last scan: " + str(last_scan) + ". The lead hunter has not found any real prospects. Do you want me to run a fresh hunt?'")
        lines.append("- DO NOT invent Reddit posts, Twitter handles, Product Hunt entries, HOT/WARM/COLD ratings, or any fictional prospect. That is fabrication and is forbidden.")
    else:
        lines.append(f"- First 5 real leads (cite from this list only, do not invent):")
        for i, lead in enumerate(leads[:5], 1):
            lines.append(f"  {i}. {json.dumps(lead)[:300]}")
    return "\n".join(lines) + "\n"




# ---------- Persistent people memory ----------
# Every incoming user message updates memory/people/<phone>.json with the
# latest activity, so BLAI can be queried later about specific people:
# "what did Sadik ask?", "any update from family?", "show messages from Saira".
# This is the same anti-hallucination pattern as url_check / lead_check:
# real data is injected into the prompt as ground truth.

PEOPLE_DIR = MEMORY_DIR / "people"
PEOPLE_DIR.mkdir(parents=True, exist_ok=True)


def _person_file(phone: str) -> Path:
    return PEOPLE_DIR / f"{phone}.json"


def update_person_memory(phone: str, message: str):
    """Append a message to a person's profile. Auto-creates the profile."""
    if not phone or not message:
        return
    f = _person_file(phone)
    profile = {}
    if f.exists():
        try:
            profile = json.loads(f.read_text())
        except Exception:
            profile = {}

    # Hydrate name/role from identity.json on first contact (or refresh)
    user_info = IDENTITY.get("whatsappUsers", {}).get(phone, {})
    if not profile:
        profile = {
            "phone": phone,
            "name": user_info.get("name", "Unknown"),
            "role": user_info.get("role", "unknown"),
            "language": user_info.get("language", "English"),
            "first_contact": time.strftime("%Y-%m-%d"),
            "total_messages": 0,
            "recent_topics": [],
            "notes": [],
        }
    else:
        # Keep name/role current with identity.json (it's the source of truth)
        if user_info.get("name"):
            profile["name"] = user_info["name"]
        if user_info.get("role"):
            profile["role"] = user_info["role"]

    profile["last_seen"] = time.strftime("%Y-%m-%d %H:%M:%S")
    profile["total_messages"] = profile.get("total_messages", 0) + 1

    # Append a short snippet of this message; keep last 15 to avoid bloat
    snippet = (message or "").strip().replace("\n", " ")
    if len(snippet) > 200:
        snippet = snippet[:200] + "..."
    topics = profile.get("recent_topics", [])
    topics.append({"ts": profile["last_seen"], "msg": snippet})
    profile["recent_topics"] = topics[-15:]

    f.write_text(json.dumps(profile, indent=2, ensure_ascii=False))


def list_all_people() -> list:
    """Return all known person profiles, sorted by last_seen desc."""
    out = []
    for fp in PEOPLE_DIR.glob("*.json"):
        try:
            out.append(json.loads(fp.read_text()))
        except Exception:
            continue
    out.sort(key=lambda p: p.get("last_seen", ""), reverse=True)
    return out


# ---------- Person-query detection (cross-user lookups) ----------
PERSON_QUERY_SIGNALS = [
    "what did", "what has", "any update from", "any update on",
    "what is", "what are", "show me messages", "show messages from",
    "messages from", "asked me", "asking", "told you", "ask you",
    "from family", "from client", "from team", "everyone", "all people",
    "who else", "anyone else", "what about", "people memory", "memory of",
]

# Name/keyword aliases mapping to who we should look up
PERSON_ALIASES = {
    "sadik": ["sushiki", "sushi"],          # client phone may not be in identity yet
    "saira": ["sister"],
    "qadir": ["brother qadir", "kadir"],
    "ummer": ["umer", "brother ummer"],
    "hina": [],
    "zam": ["wife", "zamzam", "zam zam"],
    "rebecca": [],
    "ayesha": [],
    "majeed": ["dad", "father"],
    "zineb": [],
}

ROLE_KEYWORDS = {
    "family": ["family", "brother", "sister", "wife", "dad", "mom", "father", "mother"],
    "client": ["client", "customer", "sushiki", "sadik"],
    "team": ["team", "developer", "dev"],
    "boss": ["boss", "abdul", "hafeez"],
}


def looks_like_person_query(message: str) -> bool:
    m = (message or "").lower()
    if any(sig in m for sig in PERSON_QUERY_SIGNALS):
        return True
    # Also trigger if a known name appears alongside "ask/say/want"
    if any(verb in m for verb in ["ask", "said", "say", "want", "told"]):
        for name in PERSON_ALIASES.keys():
            if name in m:
                return True
    return False


def _matches_person(profile: dict, query_lower: str) -> bool:
    name = (profile.get("name") or "").lower()
    role = (profile.get("role") or "").lower()
    phone = profile.get("phone", "")

    # Direct phone match
    if phone and phone in query_lower:
        return True
    # Direct name fragment
    for token in name.split():
        if len(token) >= 3 and token in query_lower:
            return True
    # Alias match
    for alias_root, extras in PERSON_ALIASES.items():
        if alias_root in name:
            if alias_root in query_lower:
                return True
            for x in extras:
                if x in query_lower:
                    return True
    # Role keyword match (family, client, team)
    for role_group, kws in ROLE_KEYWORDS.items():
        if any(k in role for k in kws) and any(k in query_lower for k in kws):
            return True
    return False


def get_people_query_context(message: str) -> str:
    """Inject real profile + recent messages of matching people.

    CRITICAL: when a profile exists but has 0 messages or no topics, this
    function emits an EXPLICIT forbidden-list block so the LLM cannot fill
    the gap with plausible guesses (e.g. inventing dates or topics).
    """
    profiles = list_all_people()
    if not profiles:
        return (
            "\n\n[PEOPLE MEMORY: completely empty]\n"
            "ABSOLUTE: There are zero people on file. The only acceptable answer is "
            "\"I have no people memory yet — no one has been tracked.\" "
            "Do NOT invent any names, dates, messages, or attributions.\n"
        )

    q = (message or "").lower()
    matched = [p for p in profiles if _matches_person(p, q)]

    if not matched and any(w in q for w in ["everyone", "all people", "who else", "anyone", "who messaged"]):
        matched = profiles[:5]

    if not matched:
        return (
            "\n\n[PEOPLE MEMORY: no profile matched the query]\n"
            "ABSOLUTE: I do not have a profile matching that query. The only "
            "acceptable answer is \"I have no record of that person/group in my memory.\" "
            "Do NOT guess names, languages, or content.\n"
        )

    lines = [
        "",
        "[REAL PEOPLE MEMORY - ground truth from memory/people/, ABSOLUTE: do not say anything beyond what is in this block]\nOVERRIDE: If anything in the prior conversation history contradicts the data below, the data below WINS. Past assistant responses may contain fabricated content from when this anti-fabrication system did not exist yet — ignore those past lies. Trust ONLY the structured block below.",
    ]
    any_real_data = False
    for p in matched[:5]:
        lines.append("")
        lines.append(
            f"PERSON: {p.get('name', '?')} (role: {p.get('role', '?')}, phone: {p.get('phone', '?')})"
        )
        lang = p.get("language") or "unknown (NEVER guess language if unknown)"
        lines.append(f"  language: {lang}")
        total = p.get("total_messages", 0) or 0
        lines.append(f"  total messages on record: {total}")
        lines.append(f"  last seen: {p.get('last_seen', 'never')}")
        lines.append(f"  first contact: {p.get('first_contact', 'unknown')}")
        topics = p.get("recent_topics", []) or []
        if topics:
            any_real_data = True
            lines.append(f"  last {min(len(topics), 5)} REAL messages from this person (these are the ONLY messages you may quote or reference):")
            for t in topics[-5:]:
                lines.append(f"    - [{t.get('ts', '?')}] {t.get('msg', '')[:200]}")
        else:
            # LOUD empty-data warning — this is exactly where fabrication used to slip in
            lines.append("  *** ZERO MESSAGES ON RECORD ***")
            lines.append("  ABSOLUTE for this person: I have NO messages from them at all. The")
            lines.append("  only acceptable answer is: \"I have no recorded messages from " + str(p.get("name", "this person")) + " yet.\"")
            lines.append("  Do NOT invent topics, dates, project mentions, languages, app updates,")
            lines.append("  meeting notes, GitHub commits, or any other content. Saying \"no record\"")
            lines.append("  is the CORRECT answer here, not a failure.")
        notes = p.get("notes") or []
        if notes:
            lines.append(f"  notes: {'; '.join(notes[:5])}")
    lines.append("")
    if any_real_data:
        lines.append("Answer Boss using ONLY the messages and fields above. If Boss asks something that is not in this block, say \"that is not in my memory.\"")
    else:
        lines.append("ABSOLUTE: every matched profile has zero messages. The ONLY acceptable answer is to list the names of matched people and say \"I have no recorded messages from any of them yet.\" Inventing content is forbidden.")
    return "\n".join(lines) + "\n"



# ---------- Video transcript recall (injects prior video transcript into current turn) ----------
_VIDEO_INTAKE_RE = re.compile(r"===== BLAI VIDEO INTAKE.*?===== END VIDEO INTAKE =====", re.DOTALL)
_IMAGE_INTAKE_RE = re.compile(r"===== BLAI IMAGE INTAKE.*?===== END IMAGE INTAKE =====", re.DOTALL)
_LEGACY_VIDEO_RE = re.compile(r"\[VIDEO RECEIVED.*?\[/VIDEO\]", re.DOTALL)
_VIDEO_QUESTION_TRIGGERS = [
    # "what did they say" family
    "what did he say", "what did she say", "what did the guy say", "what did they say",
    "what did the person say", "what did the man say", "what did the woman say",
    "what did you hear", "what do you hear", "what was said",
    # summary / describe
    "summarize", "summary of", "describe the video", "describe it", "describe that", "describe what", "describe him", "describe her", "describe them",
    "what was in", "what is in", "what is in the", "what was the", "what were the",
    "about the video", "from the video", "in the video", "in the recording",
    # translate / language
    "translate", "in english", "to english", "what language",
    # quote
    "quote", "his exact words", "her exact words", "their exact words", "exact words",
    "tell me what", "tell me about",
    # generic
    "repeat what", "play back",
    # image-specific
    "what is in the image", "what is in the picture", "what is in the photo",
    "what do you see", "what can you see", "describe the image", "describe the picture",
    "describe the photo", "describe the screenshot", "what does the image",
    "what does the screenshot", "what is on the screen", "read the image", "read the screenshot",
    "in the image", "in the picture", "in the photo", "in the screenshot",
    "the image", "the picture", "the photo", "the screenshot", "the images", "the photos",
    "two images", "both images", "those images", "these images",
]

def _looks_like_video_question(message: str) -> bool:
    m = (message or "").lower()
    if len(m) < 5:
        return False
    return any(t in m for t in _VIDEO_QUESTION_TRIGGERS)

def get_recent_video_context(phone: str, message: str) -> str:
    """If user asks about a video and recent history has a transcript, return it as a ground-truth block."""
    if not _looks_like_video_question(message):
        return ""
    try:
        history = get_conversation_memory(phone, limit=15)
    except Exception:
        return ""
    for h in reversed(history):
        content = h.get("content") or ""
        m = (_VIDEO_INTAKE_RE.search(content) or
             _IMAGE_INTAKE_RE.search(content) or
             _LEGACY_VIDEO_RE.search(content))
        if m:
            block = m.group(0)
            # Extract just the speech part from the block and strip all "video" wording
            speech = ""
            lang = "unknown"
            dur = ""
            for line in block.splitlines():
                line_l = line.lower()
                if "transcript" in line_l and ":" in line:
                    speech = line.split(":", 1)[1].strip().strip('"').strip("'")
                elif '"' in line and not speech and "=====" not in line:
                    speech = line.strip().strip('"').strip("'")
                if "language" in line_l and ":" in line:
                    lang = line.split(":", 1)[1].strip()
                if "duration" in line_l and ":" in line:
                    dur = line.split(":", 1)[1].strip()
            if not speech:
                # fallback: grab the whole block
                speech = block
            return (
                "\n\n===== VERIFIED TRANSCRIPT (plain text you already have) =====\n"
                "Earlier in this conversation, the user shared a recording. Whisper transcribed it. "
                "This is the verbatim speech, as plain text, directly in your context right now:\n\n"
                "    \"" + speech.replace(chr(34), "'") + "\"\n\n"
                "Language: " + lang + ". Length: " + dur + ".\n"
                "===== END TRANSCRIPT =====\n"
                "You have the full text above. Answer the user by quoting, summarizing, or translating it. "
                "You are NOT being asked to access any media file — the words are already in your context as text.\n"
            )
    return ""
# ---------- /Video recall ----------

def think(phone: str, message: str, image_data: bytes = None, video_path: str = None) -> str:
    # ---------- VIDEO UNDERSTANDING (transcribe + prepend to message) ----------
    # If a video file arrived with this message, run Whisper transcription
    # FIRST and prepend the result to `message`, so the rest of the pipeline
    # (people memory, conversation log, LLM call) sees real ground truth
    # instead of just an empty caption like "Here is it".
    if video_path:
        try:
            from skills.understand_video import transcribe_video as _tv
            _vr = _tv(video_path)
            if _vr.get("ok") and _vr.get("transcript"):
                _lang = _vr.get("language") or "?"
                _dur = _vr.get("duration") or 0
                _video_header = (
                    "===== BLAI VIDEO INTAKE (ground truth, processed by Whisper-large-v3) =====\n"
                    "Duration: " + str(int(_dur)) + "s | Detected language: " + _lang + "\n"
                    "What the sender said in the video (literal transcript):\n"
                    "    \"" + _vr["transcript"].replace(chr(34), "'") + "\"\n"
                    "===== END VIDEO INTAKE =====\n\n"
                    "INSTRUCTION TO BLAI (not to user): The sender just shared a video. The transcript above is real — Whisper already transcribed it. "
                    "Your job: (1) give a 1-3 sentence summary in English of what was said, "
                    "(2) if non-English, include both original language and English translation, "
                    "(3) if sender is a client (Sadik/SushiKi/etc), identify any actionable issue and note it, "
                    "(4) if the user also wrote a caption/question, answer that too. "
                    "NEVER say 'I cannot access the video' — you just did, the transcript is right above.\n\n"
                    "Sender's text message (caption or follow-up):\n"
                )
                message = _video_header + (message or "")
            else:
                message = (
                    "[VIDEO RECEIVED — could not transcribe: "
                    + (_vr.get("error") or "unknown error") + "]\n"
                ) + (message or "")
        except Exception as _e:
            message = "[VIDEO RECEIVED — pipeline error: " + str(_e) + "]\n" + (message or "")
    # ---------- /VIDEO ----------
    # ---------- IMAGE UNDERSTANDING (describe + prepend to message) ----------
    if image_data:
        try:
            import tempfile as _tf
            from skills.understand_image import describe_image as _di
            with _tf.NamedTemporaryFile(suffix=".jpg", delete=False) as _tmpf:
                _tmpf.write(image_data)
                _imgpath = _tmpf.name
            _ir = _di(_imgpath, message or "")
            try:
                os.unlink(_imgpath)
            except Exception:
                pass
            if _ir.get("ok"):
                _img_header = (
                    "===== BLAI IMAGE INTAKE (ground truth, processed by " + _ir.get("provider", "vision") + ") =====\n"
                    "Visual description:\n"
                    "    " + _ir["description"].replace(chr(10), " ").strip() + "\n"
                    "===== END IMAGE INTAKE =====\n\n"
                    "INSTRUCTION: The user just shared an image. The description above is what is actually in the picture. "
                    "If the user asked a question (caption below), answer it using the description. "
                    "If no caption, give a brief 1-3 sentence summary of what you see. "
                    "NEVER say 'I cannot see images' — the description is right above.\n\n"
                    "Sender's text message (caption or follow-up):\n"
                )
                message = _img_header + (message or "")
            else:
                message = (
                    "[IMAGE RECEIVED - could not analyze: "
                    + (_ir.get("error") or "unknown error") + "]\n"
                ) + (message or "")
        except Exception as _e:
            message = "[IMAGE RECEIVED - pipeline error: " + str(_e) + "]\n" + (message or "")
    # ---------- /IMAGE ----------

    """
    Send a message to Gemini and get a response.
    Total tokens: ~1,500 (system) + conversation + message.
    vs OpenClaw: ~44,000 system overhead.
    """
    keys = get_api_keys()
    if not keys:
        return ""  # Stay silent if no keys

    # Build conversation
    history = get_conversation_memory(phone)
    context = get_context_for_user(phone)

    # Check if this message triggers a real executable skill
    real_module, real_func = find_real_skill(message)
    real_skill_result = ""
    if real_module:
        try:
            real_skill_result = execute_real_skill(real_module, real_func)
        except Exception:
            real_skill_result = ""

    # Load relevant skill knowledge based on message content
    skill_knowledge = find_relevant_skills(message)

    # If a real skill produced output, include it as context for the LLM
    if real_skill_result:
        skill_knowledge += f"\n\nREAL SKILL OUTPUT ({real_module}.{real_func}):\n{real_skill_result}"

    # Build messages for Gemini
    contents = []

    # System instruction (Gemini uses systemInstruction field)
    system_text = f"{SYSTEM_PROMPT}\n\n{context}{skill_knowledge}"

    # Add conversation history
    for msg in history:
        role = "user" if msg["role"] == "user" else "model"
        contents.append({
            "role": role,
            "parts": [{"text": msg["content"]}]
        })

    # Add current message
    current_parts = [{"text": message}]
    if image_data:
        import base64
        current_parts.append({
            "inlineData": {
                "mimeType": "image/jpeg",
                "data": base64.b64encode(image_data).decode()
            }
        })
    contents.append({"role": "user", "parts": current_parts})

    # Save user message
    save_conversation(phone, "user", message)

    # Persistent people memory: append this message to the sender's profile.
    # Runs for EVERY user (Boss, family, clients, strangers) so the cross-user
    # query layer below has real data to draw from.
    try:
        update_person_memory(phone, message)
    except Exception:
        pass

    # SELF-IMPROVEMENT: if Boss is correcting us, persist the lesson forever.
    if is_boss(phone) and looks_like_correction(message):
        save_boss_correction(message)
    # MANUAL PROVIDER SWITCH (Boss-only, deterministic, no LLM call):
    # Boss can flip between providers from WhatsApp without hitting the
    # LLM at all. Useful when one provider is misbehaving and Boss wants
    # to force the other.
    if is_boss(phone):
        ml = (message or "").strip().lower()
        groq_triggers = ["switch to groq", "use groq", "force groq", "groq please", "switch groq", "go groq", "groq mode", "flip to groq", "change to groq"]
        if any(t == ml or (t in ml and len(ml) < 40) for t in groq_triggers):
            state = get_brain_state()
            state["active_provider"] = "groq"
            state["gemini_exhausted_at"] = int(time.time())  # block gemini probes
            save_brain_state(state)
            save_conversation(phone, "assistant", "Switched to Groq, Boss. Active provider is now groq.")
            return "Switched to Groq, Boss. Active provider is now groq."
        gemini_triggers = ["switch to gemini", "use gemini", "force gemini", "gemini please", "switch gemini", "go gemini", "gemini mode", "flip to gemini", "change to gemini", "back to gemini"]
        if any(t == ml or (t in ml and len(ml) < 40) for t in gemini_triggers):
            state = get_brain_state()
            state["active_provider"] = "gemini"
            state["gemini_exhausted_at"] = 0
            save_brain_state(state)
            save_conversation(phone, "assistant", "Switched to Gemini, Boss. Active provider is now gemini.")
            return "Switched to Gemini, Boss. Active provider is now gemini."
        if ml in ("provider status", "which provider", "what provider"):
            state = get_brain_state()
            return f"Active provider: {state.get('active_provider','?')}. Gemini exhausted at: {state.get('gemini_exhausted_at',0)}. Groq exhausted at: {state.get('groq_exhausted_at',0)}."

            # MEDIA ACTION HARD INTERCEPT (Boss-only, deterministic, no LLM call):
    # BLAI has NO video upload pipeline. The current Make.com social skill
    # only handles text + image URL, not video files. If Boss asks to post,
    # share, upload, or publish a video, return the honest answer here.
    # No LLM => no fabrication possible.
    if is_boss(phone):
        ml_media = (message or "").strip().lower()
        media_action_triggers = [
            "post this video", "post the video", "post that video",
            "share this video", "share the video", "share that video",
            "upload this video", "upload the video", "upload that video",
            "publish this video", "publish the video",
            "post this on all", "post it on all", "post on all", "post to all",
            "send this video", "send the video",
            "post this video i shared", "post the video i shared",
            "share on all platform", "post on all platform",
        ]
        if any(t in ml_media for t in media_action_triggers):
            try:
                from skills.make_com import health_snapshot as _hs
                snap = _hs()
            except Exception as _e:
                snap = {"ok": False, "errors": [str(_e)]}
            if not snap.get("ok"):
                honest = "Make.com unreachable: " + ", ".join(snap.get("errors", []) or ["unknown"])
            else:
                lines = ["Real Make.com state for video posting, Boss:"]
                video_scn = None
                relevant_pkgs = {"youtube", "buffer", "facebook-pages", "instagram-business", "linkedin", "tiktok"}
                for s in snap.get("scenarios", []):
                    pkgs = set(s.get("packages", []))
                    if pkgs & relevant_pkgs:
                        flag = "ON" if s["active"] else "OFF"
                        if s["invalid"]:
                            flag += "/INVALID"
                        lines.append("  - " + s["name"] + " [" + flag + "] (id " + str(s["id"]) + ")")
                        if not video_scn and (pkgs & {"youtube", "buffer"}):
                            video_scn = s
                lines.append("")
                if video_scn and video_scn.get("active") and not video_scn.get("invalid"):
                    lines.append("The YouTube/Buffer pipeline IS active and valid. To actually post your WhatsApp video I still need: (a) videoMessage download wired in whatsapp.js, (b) the file hosted somewhere with a public URL. Want me to build those two pieces now?")
                else:
                    lines.append("Both posting scenarios are currently OFF and INVALID in Make.com. Open https://eu1.make.com/scenarios in a browser, fix the connection errors, and toggle them ON. Once they are green, I can trigger them automatically.")
                honest = "\n".join(lines)
            save_conversation(phone, "assistant", honest)
            return honest

        # "DID YOU POST?" honesty check — verify against the real log
        if any(p in ml_media for p in ["did you post", "have you posted", "was it posted", "is it posted", "already posted"]):
            try:
                logp = Path("/home/tonny/blai-v2/memory/social_posts_log.json")
                if logp.exists():
                    posts = json.loads(logp.read_text() or "[]")
                    recent = [pp for pp in posts if int(time.time()) - int(pp.get("ts", 0)) < 3600]
                    if recent:
                        msg_out = "Yes — " + str(len(recent)) + " post(s) in the last hour. Most recent: " + str(recent[-1].get("platform","?"))
                        save_conversation(phone, "assistant", msg_out)
                        return msg_out
            except Exception:
                pass
            honest = "No, I have not posted anything. There is no entry in the social_posts log. I do not have a working video upload pipeline either."
            save_conversation(phone, "assistant", honest)
            return honest

    # SELF-INTROSPECTION: if Boss asks about our model/state, inject real facts
    # into the system prompt so BLAI answers from runtime truth, not from memory.
    if is_boss(phone) and looks_like_introspection(message):
        system_text = system_text + get_self_status()

    # Mood-aware response: feed Boss recent emotional trend
    if is_boss(phone):
        system_text = system_text + get_mood_context(phone)

    # Transcript recall: if user asks about a recent recording, OVERRIDE the
    # bloated system_text with a minimal transcript-only prompt. This avoids
    # the LLM pattern-matching on warning rules and refusing.
    _vctx = get_recent_video_context(phone, message)
    if _vctx:
        system_text = (
            "You are BLAI, Abdul Hafeez's AI assistant. You answer from the transcript below.\n"
            + _vctx +
            "\nAnswer the user's question by quoting, summarizing, or translating the transcript. "
            "Be direct. One or two short sentences. Never say you cannot access media — the text is already above."
        )

    # Anti-hallucination: if the message contains a URL, fetch real HTTP status
    # via curl and inject as ground truth. Stops BLAI from inventing fake URL diagnoses.
    _url_ctx = get_url_check_context(message)
    if _url_ctx:
        system_text = system_text + _url_ctx

    # Anti-hallucination: if the message is about leads, inject the REAL
    # leads.json contents so BLAI cannot fabricate fictional prospects.
    if looks_like_lead_question(message):
        system_text = system_text + get_real_lead_context()

    # People memory: if Boss is asking about someone else, inject their
    # real profile + recent messages so BLAI cannot fabricate or claim
    # ignorance when the data is right there on disk.
    if is_boss(phone) and looks_like_person_query(message):
        system_text = system_text + get_people_query_context(message)

    # Smart provider switching:
    #   - If Gemini is active, try it first; fall back to Groq on total failure.
    #   - If Groq is active (Gemini was exhausted), skip Gemini until the retry
    #     window passes, then probe it to see if the quota reset.
    state = get_brain_state()
    active = state.get("active_provider", "gemini")

    try_gemini_first = (active == "gemini") or should_probe_gemini(state)

    if try_gemini_first:
        reply = _call_gemini(system_text, contents)
        if reply:
            mark_provider("gemini")
            return _finalize_with_mood(save_conversation, phone, reply, message, is_boss(phone))
        # Gemini failed — fall through to Groq
        reply = _call_groq(system_text, history, message)
        if reply:
            mark_provider("groq")
            return _finalize_with_mood(save_conversation, phone, reply, message, is_boss(phone))
    else:
        # Currently on Groq, retry window hasn't passed — go straight to Groq
        reply = _call_groq(system_text, history, message)
        if reply:
            return _finalize_with_mood(save_conversation, phone, reply, message, is_boss(phone))
        # Groq also failed — last-ditch Gemini probe
        reply = _call_gemini(system_text, contents)
        if reply:
            mark_provider("gemini")
            return _finalize_with_mood(save_conversation, phone, reply, message, is_boss(phone))

    return ""


# Slim system prompt for background tasks. think_simple is used by content
# generation, sentiment classification, and other one-shot tasks that don't
# need the full anti-fabrication scaffolding. Keeping this short prevents
# Groq's 6000 TPM per-request ceiling from rejecting every call.
BACKGROUND_SYSTEM_PROMPT = (
    "You are BLAI, the AI working for Black Layers (blacklayers.ca), an iOS "
    "app development company by Abdul Hafeez. Brand voice: confident but "
    "humble, no corporate jargon, no fake stats. NEVER fabricate facts, "
    "stats, dates, project names, or client names. If you don't know "
    "something, say so. Output only what was asked — no preamble, no "
    "'Here is the draft:', no quotes around the result."
)


def think_simple(prompt: str) -> str:
    """One-shot call for background tasks. Mirrors the same Gemini -> Groq
    70b -> Groq 8b-instant cascade as the main think() path, with a slim
    background system prompt."""
    sys_text = BACKGROUND_SYSTEM_PROMPT

    # Pass 1: Gemini (only if not marked exhausted)
    state = get_brain_state()
    active = state.get("active_provider", "gemini")
    if active == "gemini" or should_probe_gemini(state):
        keys = get_api_keys()
        all_429 = True
        for key in keys:
            try:
                resp = requests.post(
                    f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-lite:generateContent?key={key}",
                    json={
                        "systemInstruction": {"parts": [{"text": sys_text}]},
                        "contents": [{"role": "user", "parts": [{"text": prompt}]}],
                        "generationConfig": {"maxOutputTokens": 1500, "temperature": 0.7},
                    },
                    timeout=30,
                )
                if resp.status_code == 200:
                    mark_provider("gemini")
                    return resp.json()["candidates"][0]["content"]["parts"][0]["text"]
                if resp.status_code != 429:
                    all_429 = False
            except Exception:
                all_429 = False
                continue
        if all_429:
            mark_exhausted("gemini")

    # Pass 2: Groq 70b (full prompt) on every key
    keys = get_groq_keys()
    all_429 = True
    for groq_key in keys:
        try:
            resp = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={"Authorization": f"Bearer {groq_key}", "Content-Type": "application/json"},
                json={
                    "model": "llama-3.3-70b-versatile",
                    "messages": [
                        {"role": "system", "content": sys_text},
                        {"role": "user", "content": prompt[:6000]},
                    ],
                    "max_tokens": 1500,
                    "temperature": 0.7,
                },
                timeout=30,
            )
            if resp.status_code == 200:
                mark_provider("groq")
                return resp.json()["choices"][0]["message"]["content"]
            if resp.status_code not in (429, 413):
                all_429 = False
        except Exception:
            all_429 = False
            continue

    # Pass 3: Groq 8b-instant with TRIMMED prompt (stay under 6k TPM ceiling)
    short_prompt = prompt[:3500]
    for groq_key in keys:
        try:
            resp = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={"Authorization": f"Bearer {groq_key}", "Content-Type": "application/json"},
                json={
                    "model": "llama-3.1-8b-instant",
                    "messages": [
                        {"role": "system", "content": sys_text},
                        {"role": "user", "content": short_prompt},
                    ],
                    "max_tokens": 800,
                    "temperature": 0.7,
                },
                timeout=30,
            )
            if resp.status_code == 200:
                mark_provider("groq")
                return resp.json()["choices"][0]["message"]["content"]
            if resp.status_code not in (429, 413):
                all_429 = False
        except Exception:
            all_429 = False
            continue

    if all_429:
        mark_exhausted("groq")
    return ""
