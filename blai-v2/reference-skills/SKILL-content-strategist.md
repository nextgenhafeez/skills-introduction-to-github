# SKILL: Content Strategist

Combines real trending data + project registry + brand voice into
platform-specific content drafts. Drafts saved to `memory/content_drafts/`
for Boss review BEFORE posting.

## Functions
- `content_strategist.draft_post(focus, platform)` — single draft
- `content_strategist.draft_daily_batch()` — 4 drafts (Twitter/LinkedIn/IG/blog)
- `content_strategist.list_drafts(limit)` — show recent drafts

## focus values
- `"blacklayers"` — promote blacklayers.ca itself (services, hiring CTA)
- `"<project-slug>"` — promote a specific project from the registry
- `"trend"` — react to a current trending topic

## Platform rules (hardcoded)
- Twitter: max 280 chars, 1-3 hashtags, hook + CTA
- LinkedIn: max 1500 chars, professional storytelling, 3-5 hashtags
- Instagram: max 2000 chars, hook line + value + 15-20 hashtags
- Blog: title + opening hook + 3-bullet outline (not full post)

## Workflow
```
1. Boss says "draft daily content" or "promote AdClose on LinkedIn"
2. Strategist pulls trending → pulls project (if any) → pulls brand voice
3. Builds a platform-specific prompt
4. Calls brain.think_simple() (rides the same provider state machine)
5. Saves draft to memory/content_drafts/<ts>_<platform>_<focus>.json
6. Marks project as promoted in registry
7. Returns the draft text + saved path to Boss
```

## ABSOLUTE rules
- DRAFTS ONLY — never post directly. Posting goes through
  social_poster_real (Make.com webhooks). The strategist generates and
  saves; Boss approves; the poster sends.
- If LLM returns empty (both providers down), say so honestly. Do not
  fabricate a draft.
- Never invent stats, dates, projects, or client names not in identity.json
  or projects.json.
