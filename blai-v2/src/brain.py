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

# Skill router for on-demand skill loading
from src.skill_router import find_relevant_skills


def get_api_keys():
    """Load all Gemini API keys for rotation."""
    keys_file = CONFIG_DIR / "api_keys.json"
    if keys_file.exists():
        data = json.loads(keys_file.read_text())
        return data.get("gemini", [])
    # Fallback to env
    key = os.environ.get("GOOGLE_API_KEY", os.environ.get("GEMINI_API_KEY", ""))
    return [key] if key else []


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
            prefs = "\nBoss corrections/preferences:\n" + "\n".join(
                f"- {p}" for p in prefs_data.get("corrections", [])[-5:]
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


def think(phone: str, message: str, image_data: bytes = None) -> str:
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

    # Load relevant skill knowledge based on message content
    skill_knowledge = find_relevant_skills(message)

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

    # Try each API key until one works
    for i, key in enumerate(keys):
        try:
            resp = requests.post(
                f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={key}",
                json={
                    "systemInstruction": {"parts": [{"text": system_text}]},
                    "contents": contents,
                    "generationConfig": {
                        "maxOutputTokens": 2048,
                        "temperature": 0.7
                    }
                },
                timeout=30
            )

            if resp.status_code == 200:
                data = resp.json()
                reply = data["candidates"][0]["content"]["parts"][0]["text"]
                # Save assistant response
                save_conversation(phone, "assistant", reply)
                return reply
            elif resp.status_code == 429:
                # Rate limited — try next key
                continue
            else:
                continue

        except Exception as e:
            continue

    # Don't send error messages to WhatsApp — just stay silent
    return ""


def think_simple(prompt: str) -> str:
    """Simple one-shot call for background tasks (no conversation context)."""
    keys = get_api_keys()
    for key in keys:
        try:
            resp = requests.post(
                f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={key}",
                json={
                    "systemInstruction": {"parts": [{"text": SYSTEM_PROMPT}]},
                    "contents": [{"role": "user", "parts": [{"text": prompt}]}],
                    "generationConfig": {"maxOutputTokens": 4096, "temperature": 0.7}
                },
                timeout=60
            )
            if resp.status_code == 200:
                return resp.json()["candidates"][0]["content"]["parts"][0]["text"]
            elif resp.status_code == 429:
                continue
        except:
            continue
    return ""
