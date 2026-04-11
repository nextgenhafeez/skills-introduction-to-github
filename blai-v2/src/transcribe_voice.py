#!/usr/bin/env python3
"""Transcribe voice message using Gemini and translate to English."""

import sys
import os
import base64
import requests
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def transcribe(audio_path):
    # Load API keys
    keys_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config", "api_keys.json")
    keys = json.load(open(keys_file))["gemini"]

    audio_data = open(audio_path, "rb").read()
    b64 = base64.b64encode(audio_data).decode()

    for key in keys:
        try:
            resp = requests.post(
                f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-lite:generateContent?key={key}",
                json={
                    "contents": [{"role": "user", "parts": [
                        {"inlineData": {"mimeType": "audio/ogg", "data": b64}},
                        {"text": "Transcribe this voice message word for word. If the language is NOT English, provide both the original and English translation. Format:\n[Original]: the transcription\n[English]: the translation\n\nIf already in English, just provide the transcription."}
                    ]}],
                    "generationConfig": {"maxOutputTokens": 1024, "temperature": 0.2}
                },
                timeout=30
            )
            if resp.status_code == 200:
                return resp.json()["candidates"][0]["content"]["parts"][0]["text"]
            elif resp.status_code == 429:
                continue
        except:
            continue
    return None

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: transcribe_voice.py <audio_path>")
        sys.exit(1)
    result = transcribe(sys.argv[1])
    if result:
        print(result)
