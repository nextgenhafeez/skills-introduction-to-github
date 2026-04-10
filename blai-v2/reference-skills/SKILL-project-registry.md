# SKILL: Project Registry

Single source of truth for which Black Layers projects are publicly
promotable. Lives at `memory/projects.json`.

## Schema
```json
{
  "projects": [
    {
      "slug": "adclose",
      "name": "AdClose",
      "type": "iOS app",
      "url": "https://apps.apple.com/...",
      "client": null,
      "is_public": true,
      "tech": ["Swift", "SwiftUI"],
      "blurb": "Ad blocker, $10K+/month MRR",
      "highlights": ["10K+ MRR", "100K downloads"],
      "screenshots": [],
      "launched": "2023-08",
      "last_promoted": null,
      "promote_count": 0
    }
  ]
}
```

## Functions
- `project_registry.list_projects(public_only=False)`
- `project_registry.get_project(slug_or_name)` — case-insensitive
- `project_registry.add_project(name, blurb, url, tech, ...)`
- `project_registry.mark_promoted(slug)` — auto-called by content_strategist
- `project_registry.pick_next_to_promote()` — returns the project that has
  been promoted least recently (anti-spam round-robin)
- `project_registry.bootstrap_from_identity()` — seed from
  identity.json's company.portfolio if registry is empty

## Anti-spam rule
Never promote the same project twice in 7 days unless Boss explicitly says
"promote X again". `pick_next_to_promote` handles this automatically.

## ABSOLUTE: never invent projects
Only promote what is actually in the registry. If Boss asks "promote our
fintech project" and there's no fintech project in the registry, say
"no project tagged fintech in the registry — should I add one?" Never
fabricate a portfolio entry.
