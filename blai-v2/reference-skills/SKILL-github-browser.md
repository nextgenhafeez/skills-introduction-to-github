# SKILL: GitHub Repository Browser
**Goal**: Browse, read, and summarise GitHub repositories using the configured token.

## Why this exists
BLAI has a GitHub Personal Access Token (PAT) in `config/api_keys.json`, but it
previously had no skill to actually *use* it for browsing repositories. This meant
when a client or Boss asked about a project (e.g. "tell me about the CRM
Investment Platform"), the agent would say "I can't browse GitHub."

This skill fixes that by using the GitHub REST API (api.github.com).

## Capabilities
- **List repos**: See all repos for a user/org (including private ones if the token has access).
- **Get repo info**: Description, language, stars, last push date.
- **Browse files**: Navigate the directory tree of any repo.
- **Read files**: View the contents of any file (up to 1MB).
- **Read README**: Get the README for quick project understanding.
- **Search code**: Search for code patterns within a repo.
- **Summarise project**: Auto-generate a full project summary (info + files + README).
- **Client repos**: Look up repos mapped to specific clients.

## Commands
*   `list my repos`: Show all repos for the configured GitHub owner.
*   `tell me about [repo]`: Get summary info about a specific repository.
*   `show files in [repo]`: List root-level files and directories.
*   `read [file] in [repo]`: Read the contents of a specific file.
*   `search [query] in [repo]`: Search for code patterns.
*   `summarise [repo]`: Full auto-summary (info + README + file tree).
*   `client repos for [name]`: Show repos mapped to a client.
*   `project [name]`: Triggers project lookup and summarisation.

## Configuration
The skill reads from `config/api_keys.json`:
- `github`: The Personal Access Token (PAT)
- `github_owner`: Default owner/org (e.g. "nextgenhafeez")
- `client_repos`: Mapping of client names to repo lists

## Safeguards
- **NO FABRICATION**: If a repo or file doesn't exist, the agent says so.
- **TOKEN SAFETY**: The token is never exposed in responses.
- **SIZE LIMITS**: Files > 1MB are not served via the contents API.
- **TRUNCATION**: Long files are truncated for WhatsApp readability.
