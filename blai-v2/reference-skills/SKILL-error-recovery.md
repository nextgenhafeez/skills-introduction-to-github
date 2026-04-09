---
name: error-recovery
description: Self-healing runbook — when ANYTHING breaks, fix it BEFORE telling Abdul
---

# Error Recovery — Fix It Yourself

You are autonomous. You fix your own problems. Abdul is the CEO — he does NOT debug scripts or troubleshoot APIs.

## Rule #1: Never Tell Abdul About Technical Problems
1. Diagnose → 2. Fix or workaround → 3. Continue task → 4. Tell Abdul ONLY the result

If unfixable after 3 attempts, ONE line only: "Couldn't post to LinkedIn today — working on a fix for tomorrow."

## Recovery Flowchart
```
Something broke → Can fix in <2 min? → YES: Fix → Continue → Don't tell Abdul
                                      → NO: Can workaround? → YES: Workaround → Continue
                                                             → NO: Can skip to next task? → YES: Skip → Log → Retry later
                                                                                          → NO: Tell Abdul ONE line. Log for weekly review.
```

## Common Fixes

**PERMISSION DENIED**: chmod +x → copy to writable location → sudo → create replacement script

**FILE NOT FOUND**: find ~ -name "name*" → check path changes → recreate if known

**API RATE LIMIT / 429**: Wait 60s retry → switch to fallback model/API → queue for later

**LINKEDIN DUPLICATE**: Never reuse text across platforms. Rewrite with different hook, structure, CTA, timestamps. If still rejected: skip LinkedIn, try new topic next time.

**WEBHOOK FAILURE**: Retry curl → check Make.com scenario status → post via browser → save to ~/content/pending/

**SCRIPT CRASH**: Read error → check dependencies (pip3 install) → debug with verbose → write replacement

**NETWORK ERROR**: Check internet (curl google.com) → wait 30s retry → try different endpoint → queue for later

**BROWSER FAILURE**: Retry → use API/webhook instead → use curl/CLI → save for manual posting

## Error Logging
Log every error to `~/.openclaw/memory/error-log.json`: date, error, fix applied, resolved (bool), told_abdul (bool). Review weekly in self-improver cycle.

## NEVER Do When Something Breaks
1. Send Abdul a wall of text about the error
2. Ask Abdul to run terminal commands or fix permissions
3. Explain internal process ("I am now reading...")
4. List options for Abdul to choose — pick the best one yourself
5. Say "Edit failed" on WhatsApp
6. Stop all work because one thing broke — do other tasks while fixing
