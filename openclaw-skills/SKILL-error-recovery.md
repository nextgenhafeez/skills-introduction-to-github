---
name: error-recovery
description: Self-healing runbook — when ANYTHING breaks, follow these steps BEFORE even thinking about telling Abdul
---

# Error Recovery — Fix It Yourself

**You are an autonomous agent. You fix your own problems.**
Abdul is the CEO. He does NOT debug scripts, fix permissions, or troubleshoot APIs.

---

## Rule #1: Never Tell Abdul About Technical Problems

When something breaks, your job is:
1. Diagnose the problem
2. Fix it or work around it
3. Continue the task
4. Tell Abdul ONLY the result

If you absolutely cannot fix it after 3 attempts, tell Abdul in ONE line:
```
"Couldn't post to LinkedIn today — working on a fix for tomorrow."
```
NOT:
```
"Abdul, I encountered an error when trying to edit the auto-post.py script:
EACCES: permission denied. Although my AGENTS.md and SOUL.md state I have
full write access, the system is reporting a permission error for /home/tonny/
auto-post.py. This is unexpected. To resolve this, I need your help to either:
1. Grant write permissions..."
```

---

## Common Errors & How to Fix Them

### PERMISSION DENIED (EACCES)
```bash
# Try 1: Fix permissions
chmod +x /path/to/script.py
chmod 644 /path/to/file.txt

# Try 2: Copy to writable location
cp /path/to/script.py ~/my-copy-script.py
# Edit the copy, run the copy

# Try 3: Use sudo if available
sudo chmod +x /path/to/script.py

# Try 4: Create a NEW script that does the same thing
cat > ~/my-new-script.py << 'EOF'
# Your replacement script here
EOF
python3 ~/my-new-script.py
```

### FILE NOT FOUND
```bash
# Try 1: Search for it
find ~ -name "script-name*" 2>/dev/null
ls -la ~/content/ ~/scripts/ ~/.openclaw/

# Try 2: Check if path changed
which python3
locate script-name

# Try 3: Recreate the file if you know what it should contain
```

### API RATE LIMIT / 429 ERROR
```bash
# Try 1: Wait 60 seconds, retry
sleep 60 && retry

# Try 2: Switch to backup API/model (see fallback chain)

# Try 3: Queue the task for later, continue with other work
```

### LINKEDIN DUPLICATE CONTENT ERROR
This is a KNOWN issue. LinkedIn rejects posts that are too similar.

**Fix:**
1. NEVER post the same caption to LinkedIn and other platforms
2. Always rewrite LinkedIn content to be unique:
   - Different opening hook
   - Different structure (use line breaks, arrows →, bullet points)
   - Add a personal angle or question
   - Change the CTA
3. Add a timestamp or trending reference to make it unique
4. If still rejected: skip LinkedIn for this post, try a completely new topic next time

```python
# Example: Make content unique per platform
linkedin_post = f"""
{unique_hook_for_linkedin}

{rewritten_body_with_different_structure}

{different_cta}

#UniqueHashtags #NotCopied
"""
```

### MAKE.COM / WEBHOOK FAILURE
```bash
# Try 1: Retry the webhook with curl
curl -X POST "https://hook.eu1.make.com/YOUR_WEBHOOK" \
  -H "Content-Type: application/json" \
  -d '{"text": "your content", "platform": "linkedin"}'

# Try 2: Check if Make.com scenario is active
# Open browser to eu1.make.com, check scenario status

# Try 3: Post directly via browser automation instead
# Open the platform website and post manually via browser

# Try 4: Save content to ~/content/pending/ and retry later
```

### SCRIPT CRASH / PYTHON ERROR
```bash
# Try 1: Read the error message carefully, fix the bug
python3 script.py 2>&1 | tail -20

# Try 2: Check dependencies
pip3 install -r requirements.txt
pip3 install missing-package

# Try 3: Run with verbose output to debug
python3 -v script.py

# Try 4: Write a quick replacement that does the same thing
```

### NETWORK / CONNECTION ERROR
```bash
# Try 1: Check internet
curl -s https://google.com > /dev/null && echo "Internet OK" || echo "No internet"

# Try 2: Wait and retry (network issues are often temporary)
sleep 30 && retry

# Try 3: Use a different endpoint/mirror

# Try 4: Queue task for later, work on offline tasks
```

### BROWSER AUTOMATION FAILURE
```bash
# Try 1: Retry the browser action

# Try 2: Use API/webhook instead of browser

# Try 3: Use curl/CLI tool instead

# Try 4: Save content for manual posting, move to next task
```

---

## Error Recovery Flowchart

```
Something broke
    ↓
Can I fix it in < 2 minutes?
    ↓ YES → Fix it → Continue → Don't tell Abdul
    ↓ NO
        ↓
Can I work around it?
    ↓ YES → Use workaround → Continue → Don't tell Abdul
    ↓ NO
        ↓
Can I skip this and do the next task?
    ↓ YES → Skip → Log the error → Try again later
    ↓ NO
        ↓
Tell Abdul in ONE line: "Couldn't do X, working on fix."
Log the error for weekly review.
```

---

## Error Logging

Log every error to `~/.openclaw/memory/error-log.json`:

```json
{
  "date": "2026-04-02",
  "error": "EACCES on auto-post.py",
  "fix": "Copied to ~/auto-post-v2.py with write permissions",
  "resolved": true,
  "told_abdul": false
}
```

Review this log weekly in the self-improver cycle to prevent recurring errors.

---

## What You Should NEVER Do When Something Breaks

1. **NEVER send Abdul a wall of text about the error**
2. **NEVER ask Abdul to run terminal commands**
3. **NEVER ask Abdul to change file permissions**
4. **NEVER explain your internal process** ("I am now reading the script...")
5. **NEVER list multiple options for Abdul to choose from** — pick the best one yourself
6. **NEVER say "Edit failed"** on WhatsApp — fix it and move on
7. **NEVER stop all work because one thing broke** — do the other tasks while you fix this one
