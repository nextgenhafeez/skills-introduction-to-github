"""
BLAI skill: comment review + reply engine.

HONEST SCOPE — what works today vs what needs setup:

  WORKS NOW (no extra credentials needed):
    - list_comments_inbox()      : reads memory/comments_inbox.json
    - classify_sentiment(text)   : POS / NEG / NEU / QUESTION via internal LLM
    - draft_reply(comment_id)    : generates a brand-voice reply, saves it
                                   to memory/comment_replies/<id>.json
    - list_pending_replies()     : shows drafts awaiting Boss approval
    - approve_reply(id)          : marks a draft approved (ready to send)

  REQUIRES SETUP (one-time, from Boss):
    - INGESTION: comments_inbox.json must be populated by Make.com webhook
      scenarios that watch your TikTok/Instagram/YouTube/LinkedIn accounts.
      Each scenario forwards new comments to the BLAI bridge endpoint and
      we append them here. Without those scenarios, the inbox stays empty
      and BLAI will honestly say so — no fake "you have 5 new comments".
    - SENDING: actually posting a reply back to a platform requires per-
      platform OAuth tokens (Twitter v2 API, Instagram Graph API, YouTube
      Data API). Until those are added to config/api_keys.json, this skill
      drafts and queues; sending is a manual step (Boss copies the approved
      reply to the platform).

This is exactly the anti-fabrication shape we want: every honest gap is
visible in the API surface, and BLAI cannot pretend a reply was sent.

Inbox schema (memory/comments_inbox.json):
{
  "comments": [
    {
      "id": "ig_17923_4441",
      "platform": "instagram",
      "post_id": "...",
      "post_url": "...",
      "author": "@username",
      "text": "Cool app! How much does it cost?",
      "received_at": "2026-04-10T12:34:56",
      "status": "new"   # new | drafted | approved | replied | ignored
    }
  ]
}
"""
from __future__ import annotations

import json
import sys
import time
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

INBOX_FILE = ROOT / "memory" / "comments_inbox.json"
REPLIES_DIR = ROOT / "memory" / "comment_replies"
REPLIES_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = ROOT / "memory" / "comment_engine_log.json"


def _log(entry: dict):
    entry["ts"] = time.strftime("%Y-%m-%dT%H:%M:%S")
    log = []
    if LOG_FILE.exists():
        try:
            log = json.loads(LOG_FILE.read_text())
        except Exception:
            log = []
    log.append(entry)
    log = log[-200:]
    LOG_FILE.write_text(json.dumps(log, indent=2, ensure_ascii=False))


def _load_inbox() -> dict:
    if not INBOX_FILE.exists():
        return {"comments": []}
    try:
        return json.loads(INBOX_FILE.read_text())
    except Exception:
        return {"comments": []}


def _save_inbox(data: dict):
    INBOX_FILE.parent.mkdir(parents=True, exist_ok=True)
    INBOX_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False))


# ---------- Public API ----------

def ingest_comment(platform: str, author: str, text: str, post_url: str = "", post_id: str = "") -> str:
    """
    Append a single comment to the inbox. Make.com webhook scenarios call
    this via the bridge — or Boss can call it manually for testing.
    """
    data = _load_inbox()
    cid = f"{platform[:3]}_{int(time.time())}_{str(uuid.uuid4())[:6]}"
    data["comments"].append({
        "id": cid,
        "platform": platform,
        "post_id": post_id,
        "post_url": post_url,
        "author": author,
        "text": text,
        "received_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "status": "new",
    })
    _save_inbox(data)
    _log({"op": "ingest", "id": cid, "platform": platform})
    return f"Ingested comment {cid} from {platform} ({author})."


def list_comments_inbox(status: str = "new", limit: int = 20) -> str:
    """Honest list of comments in the inbox. status='all' for everything."""
    data = _load_inbox()
    comments = data.get("comments", [])
    if status != "all":
        comments = [c for c in comments if c.get("status") == status]
    if not comments:
        if not INBOX_FILE.exists():
            return (
                "Comment inbox is empty (memory/comments_inbox.json does not exist yet). "
                "To start receiving comments, Boss needs to set up Make.com scenarios that "
                "watch each social platform and forward new comments to the BLAI bridge. "
                "I cannot fabricate fake comments — there are zero in the system right now."
            )
        return f"No comments with status='{status}'. Inbox total: {len(data.get('comments', []))}."
    lines = [f"Inbox ({len(comments)} {status} comment(s)):"]
    for c in comments[:limit]:
        lines.append(
            f"- [{c.get('id')}] {c.get('platform')} | {c.get('author')}: "
            f"{c.get('text', '')[:120]}"
        )
    return "\n".join(lines)


def classify_sentiment(text: str) -> str:
    """Use the brain to label sentiment as POS/NEG/NEU/QUESTION. Real LLM call."""
    from src import brain
    prompt = (
        "Classify this social media comment as exactly one of: POSITIVE, "
        "NEGATIVE, NEUTRAL, QUESTION. Respond with the single label only, "
        "no other text.\n\nCOMMENT: " + (text or "")[:500]
    )
    try:
        out = (brain.think_simple(prompt) or "").strip().upper()
    except Exception as e:
        return f"ERROR: {e}"
    for label in ("POSITIVE", "NEGATIVE", "NEUTRAL", "QUESTION"):
        if label in out:
            return label
    return "UNKNOWN"


def draft_reply(comment_id: str) -> str:
    """Generate a brand-voice reply for one comment. Saves to disk for review."""
    from src import brain
    data = _load_inbox()
    target = next((c for c in data.get("comments", []) if c.get("id") == comment_id), None)
    if not target:
        return f"No comment with id '{comment_id}' in inbox."

    sentiment = classify_sentiment(target.get("text", ""))

    # Pull brand voice
    try:
        ident = json.loads((ROOT / "config" / "identity.json").read_text())
    except Exception:
        ident = {}
    voice = ident.get("brandVoice", {})
    do = "; ".join(voice.get("do", [])[:5])
    dont = "; ".join(voice.get("dont", [])[:5])

    prompt = (
        f"You are replying to a {target.get('platform')} comment as Black Layers "
        f"(blacklayers.ca, iOS app development by Abdul Hafeez).\n\n"
        f"COMMENT from {target.get('author')}: {target.get('text', '')[:500]}\n"
        f"SENTIMENT: {sentiment}\n\n"
        f"BRAND VOICE — DO: {do}\n"
        f"BRAND VOICE — DON'T: {dont}\n\n"
        f"RULES:\n"
        f"- Reply in 1-2 short sentences max\n"
        f"- If it's a QUESTION about cost or hiring, point them to blacklayers.ca naturally\n"
        f"- If it's NEGATIVE, acknowledge and offer to help via DM — never argue\n"
        f"- If it's POSITIVE, thank briefly and add a small value-add (tip, fact, or related work)\n"
        f"- Never invent stats, never sound corporate, never use emoji unless the original comment used emoji\n"
        f"- OUTPUT: just the reply text, no preamble, no quotes\n"
    )
    try:
        reply_text = (brain.think_simple(prompt) or "").strip()
    except Exception as e:
        return f"LLM call failed: {e}"

    if not reply_text:
        return "LLM returned empty — both providers unavailable. Try again later."

    # Save
    out_path = REPLIES_DIR / f"{comment_id}.json"
    out_path.write_text(json.dumps({
        "comment_id": comment_id,
        "platform": target.get("platform"),
        "author": target.get("author"),
        "original": target.get("text"),
        "sentiment": sentiment,
        "draft_reply": reply_text,
        "status": "drafted",
        "created_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
    }, indent=2, ensure_ascii=False))

    target["status"] = "drafted"
    _save_inbox(data)
    _log({"op": "draft_reply", "comment_id": comment_id, "sentiment": sentiment})

    return (
        f"Draft reply for {comment_id} (sentiment: {sentiment}):\n\n"
        f"\"{reply_text}\"\n\n"
        f"Saved to: {out_path}\n"
        f"To approve: approve_reply('{comment_id}')\n"
        f"NOTE: actually posting the reply requires Boss to set up platform OAuth "
        f"tokens. Right now BLAI drafts and queues — Boss copy-pastes to the platform."
    )


def approve_reply(comment_id: str) -> str:
    out_path = REPLIES_DIR / f"{comment_id}.json"
    if not out_path.exists():
        return f"No draft for {comment_id}. Run draft_reply first."
    rec = json.loads(out_path.read_text())
    rec["status"] = "approved"
    rec["approved_at"] = time.strftime("%Y-%m-%dT%H:%M:%S")
    out_path.write_text(json.dumps(rec, indent=2, ensure_ascii=False))
    _log({"op": "approve_reply", "comment_id": comment_id})
    return (
        f"Approved reply for {comment_id}. To actually post it:\n"
        f"1. Copy this text → '{rec.get('draft_reply')}'\n"
        f"2. Paste it as a reply on the {rec.get('platform')} post\n"
        f"   OR set up the platform OAuth in config/api_keys.json so BLAI can do it directly."
    )


def list_pending_replies() -> str:
    files = sorted(REPLIES_DIR.glob("*.json"))
    if not files:
        return "No comment drafts pending."
    drafts = []
    approved = []
    for f in files:
        try:
            r = json.loads(f.read_text())
            line = f"- {r.get('comment_id')} [{r.get('platform')}] {r.get('sentiment')}: {r.get('draft_reply','')[:80]}"
            if r.get("status") == "approved":
                approved.append(line)
            else:
                drafts.append(line)
        except Exception:
            continue
    out = []
    if drafts:
        out.append(f"{len(drafts)} draft(s) awaiting approval:")
        out.extend(drafts)
    if approved:
        out.append(f"\n{len(approved)} approved (need manual posting):")
        out.extend(approved)
    return "\n".join(out) if out else "No comment drafts."
