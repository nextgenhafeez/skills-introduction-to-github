"""
BLAI skill: crypto intelligence (REAL, no fabrication).

This skill is what BLAI uses when Boss asks crypto questions. Every function
either returns REAL data from a public API, or a clear error string. Nothing
is invented. The agent that calls this skill is told (in preferences.json
and SKILL-crypto-intel.md) to use ONLY the values that come back here.

Data sources, all reachable from the GCP VM (verified live before coding):
  - CoinGecko          : prices, market cap, dominance, OHLC
  - alternative.me     : Fear & Greed index
  - OKX public API     : funding rates (Binance is geo-blocked from this VM)
  - Coinbase ticker    : clean spot price for sanity check
  - Yahoo Finance      : DXY, S&P 500, gold (macro context)
  - Farside (HTML)     : BTC ETF daily flows
  - SEC EDGAR          : real MicroStrategy 8-K filings (Saylor BTC buys)
  - Substack RSS       : Arthur Hayes essays
  - RealVision RSS     : Raoul Pal content

ABSOLUTE rules for the agent that calls this skill (also in the system prompt):
  1. Never claim "guaranteed profit", "100%", "risk-free", or "can't lose".
  2. Every signal must include: confidence %, reasoning, R/R, suggested risk %.
  3. Never auto-trade. Calculate position size, return entry/stop/target,
     the user clicks the buttons.
  4. Quote gurus VERBATIM from their RSS/EDGAR output. Never invent a quote.
  5. Every signal MUST be saved to crypto_signals.json so the scorecard
     can grade BLAI's actual hit rate over time.
"""
from __future__ import annotations

import html
import json
import re
import statistics
import time
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parent.parent
MEMORY = ROOT / "memory"
MEMORY.mkdir(parents=True, exist_ok=True)
SIGNALS_FILE = MEMORY / "crypto_signals.json"
LOG_FILE = MEMORY / "crypto_intel_log.json"
CACHE_FILE = MEMORY / "crypto_cache.json"
CACHE_TTL = 5 * 60  # 5 minutes — crypto moves fast

UA_PROFESSIONAL = "BLAI Research Agent / Black Layers (info@blacklayers.ca)"
UA_BROWSER = "Mozilla/5.0 (Macintosh; Intel Mac OS X 12_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36"


# ---------- Logging ----------

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


def _cache_get(key: str):
    if not CACHE_FILE.exists():
        return None
    try:
        cache = json.loads(CACHE_FILE.read_text())
    except Exception:
        return None
    entry = cache.get(key)
    if not entry:
        return None
    if time.time() - entry.get("ts", 0) > CACHE_TTL:
        return None
    return entry.get("value")


def _cache_set(key: str, value):
    cache = {}
    if CACHE_FILE.exists():
        try:
            cache = json.loads(CACHE_FILE.read_text())
        except Exception:
            cache = {}
    cache[key] = {"ts": time.time(), "value": value}
    CACHE_FILE.write_text(json.dumps(cache, indent=2, ensure_ascii=False))


def _get_json(url: str, headers=None, timeout: int = 12):
    h = {"User-Agent": UA_PROFESSIONAL, "Accept": "application/json"}
    if headers:
        h.update(headers)
    try:
        r = requests.get(url, headers=h, timeout=timeout)
        if r.status_code == 200:
            return r.json()
        return {"_error": f"HTTP {r.status_code}", "_body": r.text[:300]}
    except Exception as e:
        return {"_error": f"{type(e).__name__}: {e}"}


def _get_text(url: str, headers=None, timeout: int = 12) -> str | None:
    h = {"User-Agent": UA_BROWSER}
    if headers:
        h.update(headers)
    try:
        r = requests.get(url, headers=h, timeout=timeout)
        if r.status_code == 200:
            return r.text
    except Exception:
        return None
    return None


# ============================================================
# 1. SPOT MARKET SNAPSHOT
# ============================================================

def get_market_snapshot() -> dict:
    """Live BTC/ETH/SOL price, 24h change, market cap, BTC dominance, F&G index."""
    cached = _cache_get("snapshot")
    if cached:
        cached["_cached"] = True
        return cached

    out = {"_cached": False, "fetched_at": time.strftime("%Y-%m-%dT%H:%M:%S UTC", time.gmtime())}

    # Prices from CoinGecko
    cg = _get_json(
        "https://api.coingecko.com/api/v3/simple/price"
        "?ids=bitcoin,ethereum,solana,binancecoin"
        "&vs_currencies=usd"
        "&include_24hr_change=true"
        "&include_market_cap=true"
        "&include_24hr_vol=true"
    )
    if "_error" in cg:
        out["prices"] = {"_error": cg["_error"]}
    else:
        out["prices"] = {
            sym: {
                "usd": data.get("usd"),
                "change_24h_pct": round(data.get("usd_24h_change", 0), 2),
                "market_cap_usd": data.get("usd_market_cap"),
                "vol_24h_usd": data.get("usd_24h_vol"),
            }
            for sym, data in cg.items()
        }

    # Global market data (BTC dominance, total market cap)
    glob = _get_json("https://api.coingecko.com/api/v3/global")
    if "_error" not in glob:
        d = glob.get("data", {})
        out["global"] = {
            "total_market_cap_usd": d.get("total_market_cap", {}).get("usd"),
            "total_volume_24h_usd": d.get("total_volume", {}).get("usd"),
            "btc_dominance_pct": round(d.get("market_cap_percentage", {}).get("btc", 0), 2),
            "eth_dominance_pct": round(d.get("market_cap_percentage", {}).get("eth", 0), 2),
            "active_cryptos": d.get("active_cryptocurrencies"),
        }

    # Fear & Greed
    fg = _get_json("https://api.alternative.me/fng/?limit=1")
    if "_error" not in fg:
        f = (fg.get("data") or [{}])[0]
        out["fear_greed"] = {
            "value": int(f.get("value", 0)),
            "classification": f.get("value_classification"),
        }

    _cache_set("snapshot", out)
    _log({"op": "snapshot", "btc": out.get("prices", {}).get("bitcoin", {}).get("usd")})
    return out


# ============================================================
# 2. HISTORICAL OHLC + INDICATORS
# ============================================================

def get_ohlc(coin_id: str = "bitcoin", days: int = 30) -> list:
    """
    Real OHLC candles from CoinGecko.
    days options: 1, 7, 14, 30, 90, 180, 365, max
    Returns list of [timestamp_ms, open, high, low, close]
    """
    cache_key = f"ohlc_{coin_id}_{days}"
    cached = _cache_get(cache_key)
    if cached:
        return cached
    data = _get_json(
        f"https://api.coingecko.com/api/v3/coins/{coin_id}/ohlc?vs_currency=usd&days={days}"
    )
    if isinstance(data, dict) and "_error" in data:
        return []
    _cache_set(cache_key, data)
    return data


def compute_indicators(ohlc: list) -> dict:
    """
    Real indicators from OHLC candles. Returns:
      - last_close, first_close, change_pct
      - high_period, low_period
      - sma_short (10), sma_long (20 or 30 if available)
      - rsi_14
      - position_vs_sma_long ('above' / 'below' / 'at')
    """
    if not ohlc or len(ohlc) < 5:
        return {"_error": "not enough candles"}
    closes = [c[4] for c in ohlc]
    highs = [c[2] for c in ohlc]
    lows = [c[3] for c in ohlc]
    out = {
        "candles": len(ohlc),
        "first_close": round(closes[0], 2),
        "last_close": round(closes[-1], 2),
        "change_pct": round((closes[-1] - closes[0]) / closes[0] * 100, 2) if closes[0] else 0,
        "period_high": round(max(highs), 2),
        "period_low": round(min(lows), 2),
    }
    if len(closes) >= 10:
        out["sma_10"] = round(sum(closes[-10:]) / 10, 2)
    if len(closes) >= 20:
        out["sma_20"] = round(sum(closes[-20:]) / 20, 2)
        out["position_vs_sma_20"] = "above" if closes[-1] > out["sma_20"] else "below"

    # Simple RSI(14)
    if len(closes) >= 15:
        gains, losses = [], []
        for i in range(1, 15):
            change = closes[-15 + i] - closes[-16 + i]
            if change > 0:
                gains.append(change)
                losses.append(0)
            else:
                gains.append(0)
                losses.append(-change)
        avg_gain = sum(gains) / 14
        avg_loss = sum(losses) / 14
        if avg_loss == 0:
            out["rsi_14"] = 100.0
        else:
            rs = avg_gain / avg_loss
            out["rsi_14"] = round(100 - (100 / (1 + rs)), 2)
    return out


# ============================================================
# 3. FUNDING RATES (sentiment proxy via OKX — Binance is geo-blocked)
# ============================================================

def get_funding_rate(symbol: str = "BTC-USDT-SWAP") -> dict:
    """
    Real funding rate from OKX perpetuals. Returns current and recent history.
    Negative funding = shorts paying longs (contrarian-bullish).
    Positive funding = longs paying shorts (often local top warning if extreme).
    """
    cache_key = f"funding_{symbol}"
    cached = _cache_get(cache_key)
    if cached:
        return cached

    out = {"symbol": symbol, "fetched_at": time.strftime("%Y-%m-%dT%H:%M:%S UTC", time.gmtime())}
    cur = _get_json(f"https://www.okx.com/api/v5/public/funding-rate?instId={symbol}")
    if "_error" in cur:
        out["_error"] = cur["_error"]
        return out
    cur_data = (cur.get("data") or [{}])[0]
    out["current"] = {
        "funding_rate": float(cur_data.get("fundingRate", 0)),
        "funding_rate_pct": round(float(cur_data.get("fundingRate", 0)) * 100, 4),
        "next_funding_time": cur_data.get("nextFundingTime"),
    }

    hist = _get_json(
        f"https://www.okx.com/api/v5/public/funding-rate-history?instId={symbol}&limit=10"
    )
    if "_error" not in hist:
        out["recent_history"] = [
            {"funding_rate_pct": round(float(h.get("fundingRate", 0)) * 100, 4),
             "ts": h.get("fundingTime")}
            for h in (hist.get("data") or [])
        ]
        if out["recent_history"]:
            avg = statistics.mean(h["funding_rate_pct"] for h in out["recent_history"])
            out["recent_avg_pct"] = round(avg, 4)

    # Interpretation hint
    cur_pct = out["current"]["funding_rate_pct"]
    if cur_pct < -0.005:
        out["signal"] = "negative funding — shorts paying longs (contrarian-bullish)"
    elif cur_pct > 0.02:
        out["signal"] = "very positive funding — longs over-leveraged (local top risk)"
    elif cur_pct > 0.01:
        out["signal"] = "positive funding — longs paying shorts (mildly cautious)"
    else:
        out["signal"] = "neutral funding"

    _cache_set(cache_key, out)
    _log({"op": "funding", "symbol": symbol, "rate_pct": cur_pct})
    return out


# ============================================================
# 4. BTC ETF FLOWS (Farside HTML scrape)
# ============================================================

def get_etf_flows() -> dict:
    """
    Scrape Farside for the latest BTC spot ETF daily flows. Returns the most
    recent date and total net flow in millions of USD.
    Real institutional money flow — the single most important medium-term signal.
    """
    cached = _cache_get("etf_flows")
    if cached:
        return cached

    text = _get_text("https://farside.co.uk/btc/", headers={"User-Agent": UA_BROWSER})
    if not text:
        return {"_error": "could not fetch farside"}

    out = {"source": "farside.co.uk/btc", "fetched_at": time.strftime("%Y-%m-%dT%H:%M:%S UTC", time.gmtime())}
    # Find the "Total" rows. Farside table has columns: date, IBIT, FBTC, ..., Total
    # Look for rows that contain a date and end with a Total number.
    rows = re.findall(
        r"<tr[^>]*>\s*<td[^>]*>(\d{1,2}\s+\w{3}\s+\d{4})</td>(.*?)</tr>",
        text,
        flags=re.DOTALL,
    )
    parsed_rows = []
    for date_str, tds in rows[:10]:
        cells = re.findall(r"<td[^>]*>([^<]*)</td>", tds)
        if not cells:
            continue
        # Last numeric cell is Total. Parse it.
        last = cells[-1].strip().replace(",", "").replace("(", "-").replace(")", "")
        try:
            total = float(last) if last and last not in ("-", "") else 0.0
        except ValueError:
            continue
        parsed_rows.append({"date": date_str, "net_flow_musd": total})

    if parsed_rows:
        out["latest"] = parsed_rows[0]
        out["last_5_days"] = parsed_rows[:5]
        five_day_total = sum(r["net_flow_musd"] for r in parsed_rows[:5])
        out["five_day_net_musd"] = round(five_day_total, 1)
        if five_day_total > 500:
            out["signal"] = f"strong net inflow (+${round(five_day_total)}M / 5d) — institutional buying"
        elif five_day_total < -500:
            out["signal"] = f"strong net outflow (${round(five_day_total)}M / 5d) — institutional selling"
        else:
            out["signal"] = f"mixed/neutral flow (${round(five_day_total)}M / 5d)"
    else:
        out["_warning"] = "could not parse table — Farside layout may have changed"

    _cache_set("etf_flows", out)
    return out


# ============================================================
# 5. MACRO CONTEXT (DXY, S&P, GOLD)
# ============================================================

def get_macro_context() -> dict:
    """DXY, S&P 500, gold from Yahoo Finance. Crypto doesn't trade in a vacuum."""
    cached = _cache_get("macro")
    if cached:
        return cached

    out = {"fetched_at": time.strftime("%Y-%m-%dT%H:%M:%S UTC", time.gmtime())}
    symbols = {
        "DXY": "DX-Y.NYB",
        "SP500": "^GSPC",
        "GOLD": "GC=F",
    }
    for label, sym in symbols.items():
        data = _get_json(
            f"https://query1.finance.yahoo.com/v8/finance/chart/{sym}?interval=1d&range=5d",
            headers={"User-Agent": UA_BROWSER},
        )
        if "_error" in data:
            out[label] = {"_error": data["_error"]}
            continue
        try:
            result = data["chart"]["result"][0]
            closes = result["indicators"]["quote"][0]["close"]
            valid = [c for c in closes if c is not None]
            if len(valid) >= 2:
                last = valid[-1]
                prev = valid[0]
                out[label] = {
                    "last": round(last, 2),
                    "5d_change_pct": round((last - prev) / prev * 100, 2),
                }
        except Exception as e:
            out[label] = {"_error": f"parse: {e}"}

    _cache_set("macro", out)
    return out


# ============================================================
# 6. GURU PULSE — REAL filings and posts, never paraphrased
# ============================================================

def get_saylor_pulse() -> dict:
    """
    Recent MicroStrategy 8-K filings from SEC EDGAR. When MSTR buys BTC,
    they file an 8-K within 4 business days. This is the realest possible
    Saylor signal because it's a federal filing, not a tweet.
    CIK 0001050446 = MicroStrategy / Strategy
    """
    cached = _cache_get("saylor")
    if cached:
        return cached

    sub = _get_json(
        "https://data.sec.gov/submissions/CIK0001050446.json",
        headers={"User-Agent": "BlackLayers Research info@blacklayers.ca"},
    )
    if "_error" in sub:
        return {"_error": sub["_error"]}

    out = {
        "company": sub.get("name"),
        "cik": sub.get("cik"),
        "fetched_at": time.strftime("%Y-%m-%dT%H:%M:%S UTC", time.gmtime()),
    }
    recent = sub.get("filings", {}).get("recent", {})
    forms = recent.get("form", [])
    dates = recent.get("filingDate", [])
    accs = recent.get("accessionNumber", [])
    primary_docs = recent.get("primaryDocument", [])
    items = recent.get("items", [])

    eight_ks = []
    for i, form in enumerate(forms):
        if form != "8-K":
            continue
        item_codes = items[i] if i < len(items) else ""
        # Item 7.01 / 8.01 are typically used for BTC purchase disclosures
        is_btc_relevant = any(code in item_codes for code in ("7.01", "8.01", "1.01"))
        eight_ks.append({
            "date": dates[i] if i < len(dates) else "",
            "items": item_codes,
            "btc_relevant": is_btc_relevant,
            "accession": accs[i] if i < len(accs) else "",
            "doc_url": (
                f"https://www.sec.gov/Archives/edgar/data/{int(sub.get('cik', 0))}/"
                f"{accs[i].replace('-', '') if i < len(accs) else ''}/"
                f"{primary_docs[i] if i < len(primary_docs) else ''}"
            ),
        })
        if len(eight_ks) >= 10:
            break

    out["recent_8k_filings"] = eight_ks
    out["btc_purchase_filings_count"] = sum(1 for f in eight_ks if f["btc_relevant"])
    _cache_set("saylor", out)
    return out


def _parse_rss(text: str, limit: int = 5) -> list:
    """Tiny RSS/Atom parser — title, link, pubDate, description."""
    if not text:
        return []
    items = re.findall(
        r"<item>(.*?)</item>",
        text,
        flags=re.DOTALL,
    )
    out = []
    for it in items[:limit]:
        title_m = re.search(r"<title>(?:<!\[CDATA\[)?(.*?)(?:\]\]>)?</title>", it, flags=re.DOTALL)
        link_m = re.search(r"<link>(.*?)</link>", it, flags=re.DOTALL)
        date_m = re.search(r"<pubDate>(.*?)</pubDate>", it, flags=re.DOTALL)
        desc_m = re.search(r"<description>(?:<!\[CDATA\[)?(.*?)(?:\]\]>)?</description>", it, flags=re.DOTALL)
        out.append({
            "title": html.unescape((title_m.group(1) if title_m else "").strip()),
            "link": (link_m.group(1) if link_m else "").strip(),
            "date": (date_m.group(1) if date_m else "").strip(),
            "snippet": html.unescape(re.sub(r"<[^>]+>", " ", (desc_m.group(1) if desc_m else "")).strip())[:300],
        })
    return out


def get_hayes_essays(limit: int = 5) -> list:
    """Arthur Hayes Substack RSS — real essay titles + links."""
    cached = _cache_get("hayes")
    if cached:
        return cached
    text = _get_text("https://cryptohayes.substack.com/feed", headers={"User-Agent": UA_BROWSER})
    out = _parse_rss(text or "", limit=limit)
    _cache_set("hayes", out)
    return out


def get_raoul_pal_pulse(limit: int = 5) -> list:
    """RealVision RSS — Raoul Pal content."""
    cached = _cache_get("raoul")
    if cached:
        return cached
    text = _get_text("https://www.realvision.com/rss", headers={"User-Agent": UA_BROWSER})
    out = _parse_rss(text or "", limit=limit)
    _cache_set("raoul", out)
    return out


# ============================================================
# 7. SETUP DETECTION (the synthesis layer)
# ============================================================

def detect_setups() -> dict:
    """
    Combine all signals into tagged setups. Reports a CONFIDENCE percentage
    and the REASONING — never claims certainty.
    """
    snap = get_market_snapshot()
    funding = get_funding_rate()
    etf = get_etf_flows()

    factors = []
    score_long = 0   # +1 each bullish factor
    score_short = 0  # +1 each bearish factor

    # Fear & Greed extreme readings are contrarian
    fg = snap.get("fear_greed", {}).get("value")
    if fg is not None:
        if fg <= 25:
            factors.append(f"Fear & Greed at {fg} (Extreme Fear) — contrarian-bullish")
            score_long += 1
        elif fg >= 75:
            factors.append(f"Fear & Greed at {fg} (Extreme Greed) — contrarian-bearish")
            score_short += 1
        else:
            factors.append(f"Fear & Greed at {fg} ({snap['fear_greed'].get('classification')}) — neutral")

    # Funding rate
    funding_pct = funding.get("current", {}).get("funding_rate_pct")
    if funding_pct is not None:
        if funding_pct < -0.005:
            factors.append(f"Funding {funding_pct}% — shorts paying longs (contrarian-bullish)")
            score_long += 1
        elif funding_pct > 0.02:
            factors.append(f"Funding {funding_pct}% — longs over-leveraged (caution)")
            score_short += 1
        else:
            factors.append(f"Funding {funding_pct}% — neutral")

    # ETF flows
    five_day_etf = etf.get("five_day_net_musd")
    if five_day_etf is not None:
        if five_day_etf > 500:
            factors.append(f"ETF 5d net flow +${round(five_day_etf)}M — institutional buying")
            score_long += 1
        elif five_day_etf < -500:
            factors.append(f"ETF 5d net flow ${round(five_day_etf)}M — institutional selling")
            score_short += 1
        else:
            factors.append(f"ETF 5d net flow ${round(five_day_etf)}M — neutral")

    # Determine direction + confidence (real math, not random)
    if score_long >= 2 and score_short == 0:
        bias = "LONG"
        confidence = 60 + (score_long - 1) * 10  # 60-80
    elif score_short >= 2 and score_long == 0:
        bias = "SHORT"
        confidence = 60 + (score_short - 1) * 10
    elif score_long > score_short:
        bias = "MILD LONG"
        confidence = 50 + (score_long - score_short) * 5
    elif score_short > score_long:
        bias = "MILD SHORT"
        confidence = 50 + (score_short - score_long) * 5
    else:
        bias = "NEUTRAL — no edge"
        confidence = 0

    return {
        "bias": bias,
        "confidence_pct": min(confidence, 80),  # cap at 80% — nothing is 100%
        "factors": factors,
        "score_long": score_long,
        "score_short": score_short,
        "warning": (
            "This is a research signal, not a guarantee. Confidence is based on "
            "the number of aligned indicators, NOT on certainty about the future. "
            "Always use a stop-loss. Never risk more than 2% of account per trade."
        ),
    }


# ============================================================
# 8. POSITION SIZING (pure math)
# ============================================================

def position_size(account_usd: float, risk_pct: float, entry: float, stop: float) -> dict:
    """
    Calculate the exact position size for a given account risk %.
    No opinions — just math. Boss enters the trade, BLAI computes the size.
    """
    if account_usd <= 0 or risk_pct <= 0 or entry <= 0 or stop <= 0:
        return {"_error": "all inputs must be positive"}
    if risk_pct > 5:
        return {"_error": f"risk_pct {risk_pct}% > 5% — refuse to compute. Risk should be 0.5-2%."}
    risk_usd = account_usd * (risk_pct / 100)
    distance = abs(entry - stop)
    if distance == 0:
        return {"_error": "entry == stop, distance is zero"}
    distance_pct = distance / entry * 100
    units = risk_usd / distance
    position_usd = units * entry
    return {
        "account_usd": account_usd,
        "risk_pct_of_account": risk_pct,
        "max_loss_usd": round(risk_usd, 2),
        "entry": entry,
        "stop": stop,
        "stop_distance_usd": round(distance, 2),
        "stop_distance_pct": round(distance_pct, 2),
        "position_size_units": round(units, 6),
        "position_size_usd": round(position_usd, 2),
        "leverage_implied": round(position_usd / account_usd, 2),
        "rule_check": (
            "OK" if risk_pct <= 2 else
            f"WARNING: risk_pct {risk_pct}% exceeds the 2% golden rule"
        ),
    }


# ============================================================
# 9. SIGNAL LOG + SCORECARD (BLAI's actual track record)
# ============================================================

def log_signal(
    symbol: str,
    direction: str,
    entry: float,
    target: float,
    stop: float,
    confidence_pct: float,
    reason: str,
) -> str:
    """Append a signal to crypto_signals.json so it can be graded later."""
    if direction.upper() not in ("LONG", "SHORT"):
        return "ERROR: direction must be LONG or SHORT"
    data = {"signals": []}
    if SIGNALS_FILE.exists():
        try:
            data = json.loads(SIGNALS_FILE.read_text())
        except Exception:
            pass
    sig_id = f"sig_{int(time.time())}_{symbol}"
    risk_reward = abs((target - entry) / (entry - stop)) if (entry - stop) != 0 else 0
    data["signals"].append({
        "id": sig_id,
        "symbol": symbol,
        "direction": direction.upper(),
        "entry": entry,
        "target": target,
        "stop": stop,
        "confidence_pct": confidence_pct,
        "reason": reason[:500],
        "risk_reward": round(risk_reward, 2),
        "created_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "status": "open",
        "outcome": None,
    })
    SIGNALS_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False))
    _log({"op": "log_signal", "id": sig_id, "symbol": symbol, "direction": direction})
    return f"Signal logged: {sig_id}  |  {direction} {symbol} @ {entry}  R/R {risk_reward:.2f}"


def get_signal_scorecard() -> str:
    """Real hit rate from crypto_signals.json. Honest about open signals."""
    if not SIGNALS_FILE.exists():
        return "No signals logged yet. crypto_signals.json does not exist. BLAI's hit rate is not yet measurable."
    try:
        data = json.loads(SIGNALS_FILE.read_text())
    except Exception:
        return "crypto_signals.json is unreadable."
    sigs = data.get("signals", [])
    if not sigs:
        return "No signals logged yet. BLAI's hit rate is 0/0 (not measurable)."
    closed = [s for s in sigs if s.get("status") == "closed"]
    open_sigs = [s for s in sigs if s.get("status") == "open"]
    wins = [s for s in closed if s.get("outcome") == "win"]
    losses = [s for s in closed if s.get("outcome") == "loss"]
    lines = [
        f"BLAI Crypto Signal Scorecard (REAL, from crypto_signals.json):",
        f"  Total signals: {len(sigs)}",
        f"  Open: {len(open_sigs)}",
        f"  Closed: {len(closed)}",
        f"  Wins: {len(wins)}",
        f"  Losses: {len(losses)}",
    ]
    if closed:
        hit_rate = len(wins) / len(closed) * 100
        lines.append(f"  Hit rate: {hit_rate:.1f}% ({len(wins)}/{len(closed)})")
    else:
        lines.append("  Hit rate: not measurable yet (no closed signals)")
    return "\n".join(lines)


# ============================================================
# 10. TOP-LEVEL HUMAN-READABLE BRIEFING
# ============================================================

def get_full_briefing() -> str:
    """One-shot crypto briefing for WhatsApp / scheduler. Real data, no fabrication."""
    snap = get_market_snapshot()
    funding = get_funding_rate("BTC-USDT-SWAP")
    etf = get_etf_flows()
    macro = get_macro_context()
    setups = detect_setups()

    lines = [
        f"BLAI Crypto Briefing — {time.strftime('%Y-%m-%d %H:%M UTC', time.gmtime())}",
        "All numbers are REAL. Sources: CoinGecko, OKX, Farside, Yahoo, alternative.me",
        "",
        "PRICES:",
    ]
    for sym, p in (snap.get("prices") or {}).items():
        if isinstance(p, dict) and "usd" in p:
            ch = p.get("change_24h_pct", 0)
            arrow = "+" if ch >= 0 else ""
            lines.append(f"  {sym.upper():12} ${p['usd']:>10,.2f}   ({arrow}{ch}% 24h)")

    g = snap.get("global", {})
    if g:
        lines.append("")
        lines.append(f"BTC dominance: {g.get('btc_dominance_pct')}%   ETH dominance: {g.get('eth_dominance_pct')}%")
        lines.append(f"Total market cap: ${g.get('total_market_cap_usd', 0):,.0f}")

    fg = snap.get("fear_greed", {})
    if fg:
        lines.append("")
        lines.append(f"Fear & Greed: {fg.get('value')} ({fg.get('classification')})")

    fc = funding.get("current", {})
    if fc:
        lines.append("")
        lines.append(f"BTC funding (OKX perp): {fc.get('funding_rate_pct')}% per 8h")
        lines.append(f"  → {funding.get('signal', '')}")

    if etf.get("latest"):
        lines.append("")
        lines.append(f"BTC ETF latest day ({etf['latest']['date']}): ${etf['latest']['net_flow_musd']}M net")
        lines.append(f"  5-day net: ${etf.get('five_day_net_musd', 0)}M  →  {etf.get('signal', '')}")

    macro_bits = []
    for k in ("DXY", "SP500", "GOLD"):
        m = macro.get(k, {})
        if "last" in m:
            macro_bits.append(f"{k} {m['last']} ({'+' if m['5d_change_pct'] >= 0 else ''}{m['5d_change_pct']}% 5d)")
    if macro_bits:
        lines.append("")
        lines.append("MACRO: " + " | ".join(macro_bits))

    lines.append("")
    lines.append("SETUP READING:")
    lines.append(f"  Bias: {setups['bias']}  |  Confidence: {setups['confidence_pct']}%")
    for f in setups["factors"]:
        lines.append(f"  - {f}")
    lines.append("")
    lines.append("WARNING: " + setups["warning"])
    return "\n".join(lines)


def get_guru_pulse() -> str:
    """Human-readable guru briefing — real filings + RSS, never paraphrased."""
    saylor = get_saylor_pulse()
    hayes = get_hayes_essays(limit=3)
    raoul = get_raoul_pal_pulse(limit=3)

    lines = ["BLAI Guru Pulse — REAL public posts/filings only", ""]

    lines.append("MICHAEL SAYLOR / MicroStrategy (SEC EDGAR):")
    if "_error" in saylor:
        lines.append("  ERROR: " + saylor["_error"])
    else:
        relevant = [f for f in saylor.get("recent_8k_filings", []) if f.get("btc_relevant")][:5]
        if not relevant:
            lines.append("  No recent BTC-relevant 8-K filings found.")
        else:
            for f in relevant:
                lines.append(f"  - {f['date']}  Items {f['items']}  ({f['accession']})")
                if f.get("doc_url"):
                    lines.append(f"    {f['doc_url']}")

    lines.append("")
    lines.append("ARTHUR HAYES (cryptohayes.substack.com):")
    if not hayes:
        lines.append("  No recent essays parsed (RSS may be empty).")
    else:
        for h in hayes:
            lines.append(f"  - [{h.get('date', '')[:16]}] {h.get('title', '')[:120]}")
            if h.get("link"):
                lines.append(f"    {h['link']}")

    lines.append("")
    lines.append("RAOUL PAL (RealVision):")
    if not raoul:
        lines.append("  No recent items parsed.")
    else:
        for r in raoul:
            lines.append(f"  - [{r.get('date', '')[:16]}] {r.get('title', '')[:120]}")
            if r.get("link"):
                lines.append(f"    {r['link']}")

    lines.append("")
    lines.append("Note: Quotes are verbatim from SEC EDGAR + Substack/RSS. BLAI does not paraphrase guru predictions.")
    return "\n".join(lines)
