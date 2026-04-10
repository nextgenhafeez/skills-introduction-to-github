# SKILL: Comment Review + Reply Engine

HONEST scope: BLAI can ingest, classify, and draft replies to comments
right now. Actually POSTING the reply back to a platform requires per-
platform OAuth tokens that aren't in config/api_keys.json yet. Until those
are added, the workflow is: BLAI drafts → Boss approves → Boss copy-pastes
to the platform.

## What works today
- `comment_engine.ingest_comment(platform, author, text, ...)` —
  appends to memory/comments_inbox.json. Called by Make.com webhook
  scenarios that watch each platform.
- `comment_engine.list_comments_inbox(status="new")` — honest list of
  what's actually in the inbox.
- `comment_engine.classify_sentiment(text)` — POS/NEG/NEU/QUESTION
  via brain.think_simple().
- `comment_engine.draft_reply(comment_id)` — generates a brand-voice
  reply, saves to memory/comment_replies/<id>.json, marks the comment
  as 'drafted'.
- `comment_engine.list_pending_replies()` — shows drafts awaiting
  Boss approval AND approved drafts that need manual posting.
- `comment_engine.approve_reply(comment_id)` — marks a draft approved.

## What needs setup (one-time, by Boss)
1. **Comment ingestion via Make.com**: build scenarios for each platform
   that watch your account for new comments and POST them to the BLAI
   bridge. Without this, the inbox stays empty and BLAI will say so —
   never fake "you have 5 new comments".
2. **Platform OAuth for sending replies**: Twitter v2 API,
   Instagram Graph API, YouTube Data API. Once those are in
   config/api_keys.json under their own keys, we add a real
   `send_reply()` function and the workflow becomes fully automated.

## ABSOLUTE rules
- NEVER invent comments. If `list_comments_inbox` is empty, the inbox
  is genuinely empty.
- NEVER claim a reply was sent unless an approve_reply + actual platform
  POST happened. Saying "I replied to 5 comments" when none were posted
  is the worst possible failure.
- NEG sentiment → acknowledge, offer DM, never argue. POS → thank +
  small value-add. QUESTION → answer briefly + point to blacklayers.ca.
