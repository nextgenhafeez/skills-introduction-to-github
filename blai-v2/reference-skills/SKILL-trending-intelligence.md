# SKILL: Trending Intelligence (REAL)

Pulls real trending content from public APIs the VM can reach:
  - Hacker News (firebaseio, no auth)
  - GitHub Trending (HTML scrape, daily, swift + python)
  - Dev.to API (top articles per tag)
  - Product Hunt RSS

Reddit is NOT used because Reddit blocks Google Cloud IPs unless we register
an OAuth app. If Boss wants Reddit later, register at
https://www.reddit.com/prefs/apps and add reddit_oauth to api_keys.json.

## Public functions
- `trending.fetch_trending(topics, limit_per_source)` → dict with all sources
- `trending.get_trending_digest(topics)` → human-readable string
- `trending.match_to_blacklayers(items)` → filters to BL-relevant

## Cache
Results cached in `memory/trending_cache.json` for 30 minutes. Calling again
within that window returns the cached snapshot (marked `cached: True`).

## Use it for
- Daily content planning: pick 1-3 trending topics that map to Black Layers
  expertise (iOS, Swift, AI agents, mobile, indie hacking)
- Reddit comments / Quora answers: react to what's already getting traction
- Blog post topic selection: write about what people are searching for
- Tweet timing: piggyback on a trending HN story within 1-2 hours

## ABSOLUTE rules
- Never invent trending topics. If `relevant` is empty, say "no items
  matched Black Layers keywords this cycle". Do not fabricate Reddit or
  Twitter trends — those sources are not in our pipeline.
- Always show source + URL when citing a trend, so Boss can verify.
