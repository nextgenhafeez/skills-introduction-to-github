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

## Communication Rules (CRITICAL)
1. **NEVER POST RAW GITHUB URLS**: Do not include the `github.com` link in your response. Clients do not need to see the private repository link.
2. **NO [READ] TAGS**: Do not use any brackets or tags like `[READ]`.
3. **TRANSLATE IT TO NON-TECH (ACT AS A BUSINESS BRIDGE)**: The client is a non-technical business owner. They DO NOT care about "PostgreSQL", "NestJS framework", or "React". They only care about **what Abdul Hafeez has accomplished for them**.
4. **FOCUS ON REAL-WORLD PROGRESS**: Read the repo data and convert it into human achievements.
   - *Instead of:* "Built with Firebase and Google Cloud"
   - *Say:* "The underlying servers and database architecture have been fully set up and secured."
   - *Instead of:* "React CRM dashboard and Next.js website"
   - *Say:* "The admin control panel and the main public website are developed and integrated."
   - *Instead of:* "Status: 9 sprints finished"
   - *Say:* "Abdul has successfully completed 9 major milestones for the project."
5. **HUMAN TONE**: Write your summary as a polished, simple progress update that Boss can safely copy and paste straight to his non-technical client to show them the real-world value he delivered.
