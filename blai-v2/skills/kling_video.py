"""
BLAI skill: Kling AI video generation (REAL, not a stub).

This skill talks to https://api.klingai.com for real video generation. It is
intentionally small and boring so BLAI cannot hallucinate around it — every
function either returns real JSON from Kling or a clear error string.

Supported operations:
  - text_to_video(prompt, ...)  : generates a video from a text prompt
  - image_to_video(image, ...)  : animates a still image (used for "3D image"
                                  and "dynamic image" requests)
  - get_task(task_id)           : polls the status of a submitted job
  - wait_for_task(task_id, ...) : polls until done or a timeout
  - list_recent_tasks()         : returns tasks BLAI has generated recently
  - generate_and_wait(...)      : high-level helper used by the router —
                                  submits the job, polls, downloads the file,
                                  saves it under memory/videos/, and returns
                                  a short human-readable summary.

Auth: Kling uses JWT HS256 signed with secret_key, payload:
  { iss: access_key, exp: now+1800, nbf: now-5 }

All downloads land in memory/videos/ with a timestamped filename so BLAI can
reference the real file path when reporting back to Boss.
"""
from __future__ import annotations

import json
import os
import time
import uuid
from pathlib import Path

import jwt
import requests

ROOT = Path(__file__).resolve().parent.parent
CONFIG = json.loads((ROOT / "config" / "api_keys.json").read_text())
KLING_CFG = CONFIG.get("kling_ai", {})
BASE_URL = KLING_CFG.get("base_url", "https://api.klingai.com")

VIDEOS_DIR = ROOT / "memory" / "videos"
VIDEOS_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = ROOT / "memory" / "kling_log.json"


# ---------- Auth ----------

def _make_token() -> str:
    ak = KLING_CFG.get("access_key")
    sk = KLING_CFG.get("secret_key")
    if not ak or not sk:
        raise RuntimeError("Kling access_key or secret_key missing in config/api_keys.json")
    now = int(time.time())
    payload = {"iss": ak, "exp": now + 1800, "nbf": now - 5}
    return jwt.encode(payload, sk, algorithm="HS256", headers={"typ": "JWT"})


def _headers() -> dict:
    return {
        "Authorization": "Bearer " + _make_token(),
        "Content-Type": "application/json",
    }


# ---------- Logging ----------

def _log(entry: dict):
    """Append a structured log entry. Used by BLAI for honest reporting."""
    entry["ts"] = time.strftime("%Y-%m-%dT%H:%M:%S")
    log = []
    if LOG_FILE.exists():
        try:
            log = json.loads(LOG_FILE.read_text())
        except Exception:
            log = []
    log.append(entry)
    log = log[-100:]  # keep last 100 events
    LOG_FILE.write_text(json.dumps(log, indent=2, ensure_ascii=False))


# ---------- Core API wrappers ----------

def text_to_video(
    prompt: str,
    negative_prompt: str = "blurry, low quality, distorted, watermark, text",
    aspect_ratio: str = "9:16",
    duration: int = 5,
    mode: str = "std",
    model_name: str = "kling-v1",
) -> dict:
    """Submit a text-to-video job. Returns {ok, task_id, raw}."""
    body = {
        "model_name": model_name,
        "prompt": prompt[:2500],
        "negative_prompt": negative_prompt[:2500],
        "cfg_scale": 0.5,
        "mode": mode,
        "aspect_ratio": aspect_ratio,
        "duration": str(duration),
    }
    try:
        r = requests.post(
            BASE_URL + "/v1/videos/text2video",
            headers=_headers(),
            json=body,
            timeout=30,
        )
        data = r.json() if r.headers.get("content-type", "").startswith("application/json") else {}
        if r.status_code == 200 and data.get("code") == 0:
            tid = data.get("data", {}).get("task_id")
            _log({"op": "text2video_submit", "task_id": tid, "prompt": prompt[:100], "duration": duration, "aspect": aspect_ratio})
            return {"ok": True, "task_id": tid, "raw": data}
        _log({"op": "text2video_submit", "error": True, "http": r.status_code, "body": r.text[:500]})
        return {"ok": False, "error": f"HTTP {r.status_code}: {r.text[:400]}"}
    except Exception as e:
        _log({"op": "text2video_submit", "exception": str(e)})
        return {"ok": False, "error": f"exception: {e}"}


def image_to_video(
    image: str,
    prompt: str = "",
    negative_prompt: str = "blurry, distorted, watermark",
    duration: int = 5,
    mode: str = "std",
    model_name: str = "kling-v1",
) -> dict:
    """
    Animate a still image. `image` may be a public https URL OR a local file
    path (it will be base64-encoded). This is the endpoint BLAI should use
    for 'bring this 3D render to life' or 'make this logo dynamic' requests.
    """
    img_field: str
    img_path = Path(image) if not image.startswith("http") else None
    if img_path is not None and img_path.exists():
        import base64
        img_field = base64.b64encode(img_path.read_bytes()).decode()
    else:
        img_field = image  # URL

    body = {
        "model_name": model_name,
        "image": img_field,
        "prompt": prompt[:2500] if prompt else "",
        "negative_prompt": negative_prompt[:2500],
        "cfg_scale": 0.5,
        "mode": mode,
        "duration": str(duration),
    }
    try:
        r = requests.post(
            BASE_URL + "/v1/videos/image2video",
            headers=_headers(),
            json=body,
            timeout=60,
        )
        data = r.json() if r.headers.get("content-type", "").startswith("application/json") else {}
        if r.status_code == 200 and data.get("code") == 0:
            tid = data.get("data", {}).get("task_id")
            _log({"op": "image2video_submit", "task_id": tid, "image": str(image)[:120], "prompt": prompt[:100]})
            return {"ok": True, "task_id": tid, "raw": data}
        _log({"op": "image2video_submit", "error": True, "http": r.status_code, "body": r.text[:500]})
        return {"ok": False, "error": f"HTTP {r.status_code}: {r.text[:400]}"}
    except Exception as e:
        _log({"op": "image2video_submit", "exception": str(e)})
        return {"ok": False, "error": f"exception: {e}"}


def get_task(task_id: str, kind: str = "text2video") -> dict:
    """Poll the status of a submitted task. kind = 'text2video' or 'image2video'."""
    if not task_id:
        return {"ok": False, "error": "empty task_id"}
    endpoint = "/v1/videos/text2video/" if kind == "text2video" else "/v1/videos/image2video/"
    try:
        r = requests.get(
            BASE_URL + endpoint + task_id,
            headers=_headers(),
            timeout=15,
        )
        data = r.json() if r.headers.get("content-type", "").startswith("application/json") else {}
        if r.status_code == 200 and data.get("code") == 0:
            return {"ok": True, "raw": data.get("data", {})}
        return {"ok": False, "error": f"HTTP {r.status_code}: {r.text[:400]}"}
    except Exception as e:
        return {"ok": False, "error": f"exception: {e}"}


def wait_for_task(
    task_id: str,
    kind: str = "text2video",
    timeout_seconds: int = 600,
    poll_seconds: int = 10,
) -> dict:
    """Poll until status is 'succeed' or 'failed' or we time out."""
    start = time.time()
    last: dict = {}
    while time.time() - start < timeout_seconds:
        res = get_task(task_id, kind=kind)
        if not res.get("ok"):
            last = res
            time.sleep(poll_seconds)
            continue
        data = res["raw"]
        status = data.get("task_status") or data.get("status")
        if status in ("succeed", "succeeded", "success"):
            _log({"op": "task_done", "task_id": task_id, "status": status, "elapsed": int(time.time() - start)})
            return {"ok": True, "status": status, "raw": data}
        if status in ("failed", "fail", "error"):
            _log({"op": "task_failed", "task_id": task_id, "raw": data})
            return {"ok": False, "status": status, "raw": data, "error": data.get("task_status_msg", "failed")}
        last = {"ok": True, "status": status, "raw": data}
        time.sleep(poll_seconds)
    return {"ok": False, "error": "timeout", "last": last}


def list_recent_tasks() -> str:
    """Human-readable summary of recent Kling tasks BLAI has submitted."""
    if not LOG_FILE.exists():
        return "No Kling tasks have been run yet. Log file is empty."
    try:
        log = json.loads(LOG_FILE.read_text())
    except Exception:
        return "Kling log exists but is unreadable."
    if not log:
        return "No Kling tasks have been run yet."
    recent = log[-10:]
    lines = ["Last " + str(len(recent)) + " Kling events (REAL, from memory/kling_log.json):"]
    for e in recent:
        op = e.get("op", "?")
        ts = e.get("ts", "?")
        tid = e.get("task_id", "-")
        extra = e.get("prompt") or e.get("status") or e.get("error") or ""
        lines.append(f"- [{ts}] {op} task={tid} {str(extra)[:120]}")
    return "\n".join(lines)


# ---------- High-level helper used by BLAI skill router ----------

def generate_and_wait(
    prompt: str,
    kind: str = "text2video",
    image: str = "",
    aspect_ratio: str = "9:16",
    duration: int = 5,
    mode: str = "std",
) -> str:
    """
    One-shot generator for BLAI: submit → wait → download → return summary.
    Return value is always a short human-readable string — no JSON, no lies.
    If anything fails, the string says exactly what failed.
    """
    if kind == "image2video":
        if not image:
            return "ERROR: image2video requires an image (URL or local path) — none provided."
        sub = image_to_video(image, prompt=prompt, duration=duration, mode=mode)
    else:
        sub = text_to_video(prompt, aspect_ratio=aspect_ratio, duration=duration, mode=mode)

    if not sub.get("ok"):
        return "Kling submission failed: " + str(sub.get("error", "unknown"))

    task_id = sub.get("task_id")
    if not task_id:
        return "Kling accepted the request but returned no task_id: " + json.dumps(sub.get("raw", {}))[:300]

    res = wait_for_task(task_id, kind=kind)
    if not res.get("ok"):
        return (
            "Kling task " + str(task_id) + " did not finish: " + str(res.get("error", "?"))
            + " (status=" + str(res.get("status", "?")) + ")"
        )

    data = res.get("raw", {})
    videos = (data.get("task_result") or {}).get("videos") or []
    if not videos:
        return "Kling task " + str(task_id) + " finished but returned no video payload: " + json.dumps(data)[:400]

    video_url = videos[0].get("url", "")
    if not video_url:
        return "Kling task " + str(task_id) + " finished but no download URL was provided."

    # Download the file immediately — Kling deletes after 30 days
    try:
        vr = requests.get(video_url, timeout=120)
        if vr.status_code != 200:
            return "Kling task " + str(task_id) + " OK but download failed: HTTP " + str(vr.status_code)
        filename = time.strftime("%Y%m%d_%H%M%S") + "_" + task_id[:8] + ".mp4"
        out_path = VIDEOS_DIR / filename
        out_path.write_bytes(vr.content)
        _log({"op": "downloaded", "task_id": task_id, "path": str(out_path), "bytes": len(vr.content)})
        return (
            "Video generated successfully.\n"
            "  task_id: " + str(task_id) + "\n"
            "  prompt: " + prompt[:180] + "\n"
            "  aspect: " + str(aspect_ratio) + ", duration: " + str(duration) + "s, mode: " + str(mode) + "\n"
            "  saved to: " + str(out_path) + "\n"
            "  size: " + str(len(vr.content)) + " bytes\n"
            "  source URL (expires ~30 days): " + video_url
        )
    except Exception as e:
        return "Kling task " + str(task_id) + " OK but download exception: " + str(e)[:200]
