#!/usr/bin/env python3
"""
Image understanding skill for BLAI.
Sends image to Groq Llama-4-Scout vision (free tier, fast). Falls back to
Gemini 2.5-flash-lite if Groq fails AND Gemini quota is available.
"""
import os
import json
import base64
from pathlib import Path

import requests

CONFIG_DIR = Path(__file__).parent.parent / "config"

GROQ_VISION_MODEL = "meta-llama/llama-4-scout-17b-16e-instruct"


def _groq_keys():
    try:
        data = json.loads((CONFIG_DIR / "api_keys.json").read_text())
        g = data.get("groq", [])
        return g if isinstance(g, list) else [g]
    except Exception:
        return []


def _gemini_keys():
    try:
        data = json.loads((CONFIG_DIR / "api_keys.json").read_text())
        g = data.get("gemini", [])
        return g if isinstance(g, list) else [g]
    except Exception:
        return []


def _describe_groq(image_bytes: bytes, prompt: str) -> dict:
    b64 = base64.b64encode(image_bytes).decode()
    last_err = ""
    for k in _groq_keys():
        try:
            r = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={"Authorization": "Bearer " + k},
                json={
                    "model": GROQ_VISION_MODEL,
                    "messages": [{
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {"type": "image_url", "image_url": {"url": "data:image/jpeg;base64," + b64}},
                        ],
                    }],
                    "max_tokens": 600,
                    "temperature": 0.2,
                },
                timeout=60,
            )
            if r.status_code == 200:
                return {"ok": True, "description": r.json()["choices"][0]["message"]["content"], "provider": "groq"}
            elif r.status_code in (401, 403):
                last_err = "groq auth"
                continue
            elif r.status_code == 429:
                last_err = "groq 429"
                continue
            else:
                last_err = "groq " + str(r.status_code) + ": " + r.text[:200]
        except Exception as e:
            last_err = "groq exc: " + str(e)
    return {"ok": False, "error": last_err}


def _describe_gemini(image_bytes: bytes, prompt: str) -> dict:
    b64 = base64.b64encode(image_bytes).decode()
    for k in _gemini_keys():
        try:
            r = requests.post(
                "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-lite:generateContent?key=" + k,
                json={
                    "contents": [{"role": "user", "parts": [
                        {"inlineData": {"mimeType": "image/jpeg", "data": b64}},
                        {"text": prompt},
                    ]}],
                    "generationConfig": {"maxOutputTokens": 600, "temperature": 0.2},
                },
                timeout=60,
            )
            if r.status_code == 200:
                txt = r.json()["candidates"][0]["content"]["parts"][0]["text"]
                return {"ok": True, "description": txt, "provider": "gemini"}
            elif r.status_code == 429:
                continue
        except Exception:
            continue
    return {"ok": False, "error": "all gemini keys exhausted"}


def describe_image(image_path: str, user_caption: str = "") -> dict:
    """Returns {"ok": bool, "description": str, "provider": str, "error": str}"""
    if not os.path.exists(image_path):
        return {"ok": False, "error": "image file not found"}

    image_bytes = open(image_path, "rb").read()

    prompt = (
        "You are analyzing an image that was sent on WhatsApp. Describe what you see in detail: "
        "objects, people, text visible in the image (transcribe any text exactly), UI elements if it is a screenshot, "
        "the apparent purpose or context. If it is a screenshot of a chat, app, or document, transcribe the visible text. "
        "If the user asks you something specific, focus on that. Be concrete and factual. Max 6 lines."
    )
    if user_caption:
        prompt += "\n\nThe user wrote: " + user_caption

    # Try Groq Llama-4-Scout first (free, vision-capable, generous quota)
    out = _describe_groq(image_bytes, prompt)
    if out.get("ok"):
        return out

    # Fall back to Gemini if Groq failed
    out2 = _describe_gemini(image_bytes, prompt)
    if out2.get("ok"):
        return out2

    return {"ok": False, "error": (out.get("error", "") + " | " + out2.get("error", "")).strip(" |")}


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("usage: understand_image.py <image_path> [caption]")
        sys.exit(1)
    cap = sys.argv[2] if len(sys.argv) > 2 else ""
    out = describe_image(sys.argv[1], cap)
    print(json.dumps(out, indent=2, ensure_ascii=False))
