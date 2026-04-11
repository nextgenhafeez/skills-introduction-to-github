#!/usr/bin/env python3
"""
Video understanding skill for BLAI.
Extracts audio with ffmpeg, transcribes via Groq Whisper (free, fast).
Returns the transcript text or None on failure.
"""
import os
import json
import subprocess
import time
from pathlib import Path

import requests

CONFIG_DIR = Path(__file__).parent.parent / "config"


def _groq_keys():
    try:
        data = json.loads((CONFIG_DIR / "api_keys.json").read_text())
        g = data.get("groq", [])
        return g if isinstance(g, list) else [g]
    except Exception:
        return []


def _extract_audio(video_path: str) -> str:
    """Run ffmpeg to extract mono 16kHz mp3 audio. Returns path or None."""
    if not os.path.exists(video_path):
        return None
    out = "/tmp/blai_aud_" + str(int(time.time() * 1000)) + ".mp3"
    try:
        r = subprocess.run(
            [
                "ffmpeg", "-y", "-i", video_path,
                "-vn", "-ac", "1", "-ar", "16000", "-b:a", "32k", out,
            ],
            capture_output=True, text=True, timeout=60,
        )
        if r.returncode == 0 and os.path.exists(out) and os.path.getsize(out) > 0:
            return out
    except Exception:
        pass
    return None


def _video_duration(video_path: str) -> float:
    try:
        r = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration",
             "-of", "default=noprint_wrappers=1:nokey=1", video_path],
            capture_output=True, text=True, timeout=10,
        )
        return float((r.stdout or "0").strip())
    except Exception:
        return 0.0


def transcribe_video(video_path: str) -> dict:
    """Returns {"ok": bool, "transcript": str, "duration": float, "language": str, "error": str}"""
    result = {"ok": False, "transcript": "", "duration": 0.0, "language": "", "error": ""}

    if not os.path.exists(video_path):
        result["error"] = "video file not found"
        return result

    result["duration"] = _video_duration(video_path)

    audio = _extract_audio(video_path)
    if not audio:
        result["error"] = "ffmpeg audio extract failed"
        return result

    keys = _groq_keys()
    if not keys:
        result["error"] = "no groq keys configured"
        return result

    last_err = ""
    for k in keys:
        try:
            with open(audio, "rb") as f:
                r = requests.post(
                    "https://api.groq.com/openai/v1/audio/transcriptions",
                    headers={"Authorization": "Bearer " + k},
                    files={"file": (os.path.basename(audio), f, "audio/mpeg")},
                    data={"model": "whisper-large-v3", "response_format": "verbose_json"},
                    timeout=120,
                )
            if r.status_code == 200:
                data = r.json()
                result["ok"] = True
                result["transcript"] = (data.get("text") or "").strip()
                result["language"] = data.get("language") or ""
                break
            elif r.status_code in (401, 403):
                last_err = "auth failed"
                continue
            elif r.status_code == 429:
                last_err = "rate limited"
                continue
            else:
                last_err = "http " + str(r.status_code) + ": " + r.text[:200]
        except Exception as e:
            last_err = str(e)
            continue

    if not result["ok"] and last_err:
        result["error"] = last_err

    try:
        os.unlink(audio)
    except Exception:
        pass

    return result


# Stand-alone CLI for manual testing
if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("usage: understand_video.py <video_path>")
        sys.exit(1)
    out = transcribe_video(sys.argv[1])
    print(json.dumps(out, indent=2, ensure_ascii=False))
