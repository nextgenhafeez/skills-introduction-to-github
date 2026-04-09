# BLAI Cost Breakdown & Optimization Report

**Date:** April 9, 2026
**Prepared by:** Claude (for Abdul Hafeez / Black Layers)
**Project:** BLAI v2 — WhatsApp AI Agent on Google Cloud

---

## 1. Problem: Monthly costs hit ~$107+ CAD

BLAI was burning money across two services that should have been cheap or free.

| Service | Monthly Cost | Expected Cost |
|---------|-------------|---------------|
| Gemini API (Google AI Studio) | CA$46.09 | $0 (free tier) |
| Google Cloud (VM + services) | $61.15 USD | ~$15-20 |
| **Total** | **~$107+ CAD** | **~$15-20** |

---

## 2. Root Cause Analysis

### 2.1 Gemini API — CA$46.09 (should be $0)

**What happened:** BLAI was on **Paid Tier 1** instead of the free tier.

**Why it was expensive:**
- BLAI uses `gemini-2.5-flash` — a newer, premium model with higher per-token cost
- Only **1 API key** was configured for rotation
- When that single key hit rate limits, retries still burned the same paid quota
- No daily spending cap was set — charges accumulated unchecked
- The spend cap was set to CA$50.00 with no alerts before hitting it

**The fix:**
- Switch model from `gemini-2.5-flash` to `gemini-2.0-flash` (free-tier eligible)
- Add 3-4 API keys from separate Google Cloud projects for rotation (each gets its own free quota)
- Set spend cap to CA$0 to enforce free tier
- Result: **CA$46/month → $0/month**

---

### 2.2 Google Cloud VM — $61.15/month (should be ~$15)

**What happened:** The VM was oversized for what BLAI actually needs.

**Breakdown of VM costs:**

| Resource | Configuration | Est. Monthly Cost | Needed? |
|----------|--------------|-------------------|---------|
| VM instance (e2-medium) | 2 vCPU, 4GB RAM | ~$25.00 | No — BLAI uses <700MB RAM, <0.1 CPU load |
| Persistent disk | 100GB standard | ~$4.00 | No — only 19GB used after cleanup |
| Network (PREMIUM tier) | External IP + egress | ~$5.00 | STANDARD tier is sufficient |
| Ollama service | Running 24/7, idle | ~$0 (CPU waste) | No — BLAI only calls Gemini API |
| Ollama models on disk | 32GB of unused models | $0 (disk waste) | No — 3 of 4 models couldn't even run in 4GB RAM |
| Other GCP services | Firebase, etc. | ~$27.00 | Under investigation |

**Why it was expensive:**
- **Oversized VM:** e2-medium (2 vCPU, 4GB RAM) for an agent that uses 634MB RAM and 0.08 CPU load
- **Oversized disk:** 100GB disk when only 19GB is used (was 50GB before cleanup, 32GB was Ollama models)
- **Ollama running for nothing:** Ollama service was running 24/7 consuming resources, but BLAI v2 never calls it — it only uses Gemini API
- **4 Ollama models downloaded (32GB) that were useless:**
  - `glm-4.7-flash` (19GB) — far too large for 4GB RAM VM
  - `qwen2.5:14b` (9GB) — too large for 4GB RAM VM
  - `qwen2.5:7b` (4.7GB) — borderline, never used by BLAI
  - `qwen2.5:1.5b` (986MB) — only one that could run, but BLAI doesn't use Ollama
- **PREMIUM network tier** when STANDARD would work fine

---

## 3. Actions Taken (April 9, 2026)

### Completed

| # | Action | Impact |
|---|--------|--------|
| 1 | Deleted `glm-4.7-flash` (19GB Ollama model) | Freed 19GB disk |
| 2 | Deleted `qwen2.5:14b` (9GB Ollama model) | Freed 9GB disk |
| 3 | Deleted `qwen2.5:7b` (4.7GB Ollama model) | Freed 4.7GB disk |
| 4 | Stopped and disabled Ollama service | Freed RAM + CPU cycles |
| 5 | Kept `qwen2.5:1.5b` (986MB) as emergency local fallback | Insurance only |

**Disk usage after cleanup:** 50GB → 19GB (freed 31GB)

### Pending

| # | Action | Expected Savings |
|---|--------|-----------------|
| 6 | Switch Gemini model from `2.5-flash` → `2.0-flash` | Reduces token cost, free-tier eligible |
| 7 | Add 3-4 Gemini API keys for rotation | Eliminates rate-limit issues on free tier |
| 8 | Set Gemini spend cap to CA$0 | Prevents any future charges |
| 9 | Downsize VM from e2-medium → e2-small | Saves ~$12/month |
| 10 | Shrink disk from 100GB → 30GB | Saves ~$3/month |
| 11 | Switch network from PREMIUM → STANDARD tier | Saves ~$2-3/month |

---

## 4. Before vs After

### Cost Comparison

| Service | Before (Monthly) | After (Monthly) | Savings |
|---------|-----------------|-----------------|---------|
| Gemini API | CA$46.09 | $0 (free tier) | **CA$46** |
| VM compute (e2-medium → e2-small) | ~$25 | ~$13 | **$12** |
| Disk (100GB → 30GB) | ~$4 | ~$1.20 | **$2.80** |
| Network (PREMIUM → STANDARD) | ~$5 | ~$2 | **$3** |
| Other GCP services | ~$27 | ~$27 | $0 |
| **Total** | **~$107 CAD** | **~$43 CAD** | **~$64/month saved** |

### Resource Comparison

| Resource | Before | After |
|----------|--------|-------|
| VM type | e2-medium (2 vCPU, 4GB) | e2-small (1 vCPU, 2GB) |
| Disk | 100GB (50GB used) | 30GB (19GB used) |
| Ollama models | 4 models, 32GB | 1 model, 986MB (emergency only) |
| Ollama service | Running 24/7 | Disabled |
| Gemini API keys | 1 key (paid tier) | 4 keys (free tier, rotation) |
| Gemini model | 2.5-flash (premium) | 2.0-flash (free-tier eligible) |
| Network tier | PREMIUM | STANDARD |

---

## 5. Architecture: What BLAI Actually Runs

```
WhatsApp message
    ↓
whatsapp.js (Node.js, ~100MB RAM)
    ↓
bridge.py (spawned per message)
    ↓
brain.py → Gemini API (free tier, 4 rotating keys)
    ↓
WhatsApp reply
```

**Total VM resources needed:** <1GB RAM, <0.5 vCPU, <30GB disk.
Everything else was waste.

---

## 6. Lessons Learned

1. **Always check billing tier** — Gemini has a free tier, but the account was on Paid Tier 1 without anyone realizing
2. **One API key is a single point of failure** — rate limits on one key = either errors or paid overages
3. **Don't install models that can't run** — downloading 19GB and 9GB models on a 4GB RAM VM was pointless
4. **Right-size the VM** — an AI agent that calls external APIs doesn't need a big machine
5. **Set budget alerts** — Google Cloud has budget alerts in Billing → Budgets & alerts. Set one at $20/month
6. **Monitor spend caps** — the CA$50 Gemini cap almost got hit with no warning

---

## 7. Remaining Risks

| Risk | Mitigation |
|------|-----------|
| Free tier rate limits during peak hours | 4 API keys rotate automatically |
| All keys rate-limited simultaneously | BLAI stays silent (no error messages sent) |
| VM costs still ~$43/month | Consider scheduling VM stop during night hours (saves ~30%) |
| Other GCP services ($27) unaccounted | Need to investigate Firebase/other service costs separately |

---

*Report generated April 9, 2026. Review monthly to ensure costs stay on target.*
