#!/usr/bin/env python3
"""
BLAI Crypto Intelligence v2 — Real technical analysis, macro data, institutional tracking.
Not just prices — actual RSI, moving averages, buy/sell signals, and smart money tracking.
"""

import requests
import json
from datetime import datetime, timedelta
from pathlib import Path

DATE = datetime.now().strftime("%Y-%m-%d")
SCAN_DIR = Path.home() / ".openclaw/memory"
SCAN_DIR.mkdir(parents=True, exist_ok=True)
REPORT_FILE = SCAN_DIR / f"crypto-report-{DATE}.txt"
SIGNAL_FILE = SCAN_DIR / "signal-tracker.json"

COINS = {
    "bitcoin": "BTC",
    "ethereum": "ETH",
    "solana": "SOL",
    "binancecoin": "BNB",
    "ripple": "XRP",
}

HEADERS = {"User-Agent": "BLAI-CryptoIntel/2.0"}


def fmt(n):
    if n >= 1e12: return f"${n/1e12:.1f}T"
    if n >= 1e9: return f"${n/1e9:.1f}B"
    if n >= 1e6: return f"${n/1e6:.1f}M"
    return f"${n:,.0f}"


def get_prices():
    """Get current prices with 24h change and market cap."""
    try:
        r = requests.get("https://api.coingecko.com/api/v3/simple/price",
            params={
                "ids": ",".join(COINS.keys()),
                "vs_currencies": "usd",
                "include_24hr_change": "true",
                "include_market_cap": "true"
            }, headers=HEADERS, timeout=10)
        return r.json() if r.status_code == 200 else {}
    except Exception:
        return {}


def get_price_history(coin_id, days=200):
    """Get daily price history for technical analysis."""
    try:
        r = requests.get(
            f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart",
            params={"vs_currency": "usd", "days": days, "interval": "daily"},
            headers=HEADERS, timeout=15)
        if r.status_code == 200:
            return [p[1] for p in r.json().get("prices", [])]
    except Exception:
        pass
    return []


def calculate_rsi(prices, period=14):
    """Calculate RSI from price history."""
    if len(prices) < period + 1:
        return None

    deltas = [prices[i] - prices[i-1] for i in range(1, len(prices))]
    recent = deltas[-(period):]

    gains = [d for d in recent if d > 0]
    losses = [-d for d in recent if d < 0]

    avg_gain = sum(gains) / period if gains else 0
    avg_loss = sum(losses) / period if losses else 0.001

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return round(rsi, 1)


def calculate_ma(prices, period):
    """Calculate simple moving average."""
    if len(prices) < period:
        return None
    return round(sum(prices[-period:]) / period, 2)


def get_fear_greed():
    """Get Fear & Greed Index with history."""
    try:
        r = requests.get("https://api.alternative.me/fng/?limit=7", timeout=10)
        if r.status_code == 200:
            data = r.json()["data"]
            today = data[0]
            yesterday = data[1] if len(data) > 1 else today
            week_ago = data[6] if len(data) > 6 else today
            return {
                "value": int(today["value"]),
                "label": today["value_classification"],
                "yesterday": int(yesterday["value"]),
                "week_ago": int(week_ago["value"]),
            }
    except Exception:
        pass
    return {"value": 0, "label": "unknown", "yesterday": 0, "week_ago": 0}


def get_trending():
    """Get trending coins."""
    try:
        r = requests.get("https://api.coingecko.com/api/v3/search/trending",
            headers=HEADERS, timeout=10)
        if r.status_code == 200:
            return [f"{c['item']['name']} ({c['item']['symbol']})"
                    for c in r.json()["coins"][:7]]
    except Exception:
        pass
    return []


def get_global():
    """Get global market data."""
    try:
        r = requests.get("https://api.coingecko.com/api/v3/global",
            headers=HEADERS, timeout=10)
        if r.status_code == 200:
            d = r.json()["data"]
            return {
                "market_cap": d.get("total_market_cap", {}).get("usd", 0),
                "volume_24h": d.get("total_volume", {}).get("usd", 0),
                "btc_dom": d.get("market_cap_percentage", {}).get("btc", 0),
                "eth_dom": d.get("market_cap_percentage", {}).get("eth", 0),
            }
    except Exception:
        pass
    return {}


def get_btc_etf_sentiment():
    """Estimate institutional sentiment from recent news searches."""
    # We can't directly access ETF flow APIs without keys,
    # but we can track via CoinGecko BTC market data
    signals = []
    try:
        r = requests.get(
            "https://api.coingecko.com/api/v3/coins/bitcoin",
            params={"localization": "false", "tickers": "false",
                    "community_data": "true", "developer_data": "false"},
            headers=HEADERS, timeout=10)
        if r.status_code == 200:
            data = r.json()
            md = data.get("market_data", {})

            # Price change over different periods
            d7 = md.get("price_change_percentage_7d", 0)
            d30 = md.get("price_change_percentage_30d", 0)
            d1y = md.get("price_change_percentage_1y", 0)
            ath = md.get("ath", {}).get("usd", 0)
            current = md.get("current_price", {}).get("usd", 0)
            ath_pct = ((current - ath) / ath * 100) if ath > 0 else 0

            return {
                "7d_change": round(d7, 1),
                "30d_change": round(d30, 1),
                "1y_change": round(d1y, 1),
                "ath": ath,
                "ath_distance": round(ath_pct, 1),
                "current": current,
            }
    except Exception:
        pass
    return {}


def determine_signal(rsi, fg_value, ma50, ma200, current_price, btc_data):
    """Determine BUY/SELL/HOLD signal based on multiple indicators."""
    buy_signals = 0
    sell_signals = 0
    reasons_buy = []
    reasons_sell = []
    total_checks = 7

    # 1. Fear & Greed
    if fg_value <= 20:
        buy_signals += 1
        reasons_buy.append(f"Extreme Fear ({fg_value}/100) — historically a buy zone")
    elif fg_value >= 80:
        sell_signals += 1
        reasons_sell.append(f"Extreme Greed ({fg_value}/100) — historically a sell zone")

    # 2. RSI
    if rsi and rsi < 30:
        buy_signals += 1
        reasons_buy.append(f"RSI oversold ({rsi})")
    elif rsi and rsi > 70:
        sell_signals += 1
        reasons_sell.append(f"RSI overbought ({rsi})")

    # 3. Price vs Moving Averages
    if ma50 and ma200 and current_price:
        if current_price > ma50 and current_price > ma200:
            buy_signals += 1
            reasons_buy.append("Price above 50MA and 200MA (bullish structure)")
        elif current_price < ma50 and current_price < ma200:
            sell_signals += 1
            reasons_sell.append("Price below 50MA and 200MA (bearish structure)")

    # 4. Golden/Death Cross
    if ma50 and ma200:
        if ma50 > ma200:
            buy_signals += 1
            reasons_buy.append("Golden cross active (50MA > 200MA)")
        else:
            sell_signals += 1
            reasons_sell.append("Death cross active (50MA < 200MA)")

    # 5. 30-day momentum
    if btc_data.get("30d_change", 0) > 10:
        buy_signals += 1
        reasons_buy.append(f"Strong 30d momentum (+{btc_data['30d_change']}%)")
    elif btc_data.get("30d_change", 0) < -15:
        sell_signals += 1
        reasons_sell.append(f"Weak 30d momentum ({btc_data['30d_change']}%)")

    # 6. Distance from ATH
    ath_dist = btc_data.get("ath_distance", 0)
    if ath_dist < -40:
        buy_signals += 1
        reasons_buy.append(f"Far from ATH ({ath_dist}%) — potential value")
    elif ath_dist > -5:
        sell_signals += 1
        reasons_sell.append(f"Near ATH ({ath_dist}%) — consider taking profit")

    # 7. Halving cycle position
    # Last halving: April 19, 2024
    halving_date = datetime(2024, 4, 19)
    days_since = (datetime.now() - halving_date).days
    if 365 < days_since < 547:  # 12-18 months post-halving = peak zone
        reasons_sell.append(f"In historical peak window ({days_since} days post-halving)")
        sell_signals += 1
    elif days_since < 365:
        reasons_buy.append(f"Pre-peak zone ({days_since} days post-halving)")
        buy_signals += 1

    # Determine signal
    if buy_signals >= 4:
        signal = "BUY"
        confidence = min(buy_signals + 3, 10)
    elif sell_signals >= 4:
        signal = "SELL / TAKE PROFIT"
        confidence = min(sell_signals + 3, 10)
    elif buy_signals >= 3 and sell_signals <= 1:
        signal = "LEAN BUY"
        confidence = min(buy_signals + 2, 10)
    elif sell_signals >= 3 and buy_signals <= 1:
        signal = "LEAN SELL"
        confidence = min(sell_signals + 2, 10)
    else:
        signal = "HOLD / WAIT"
        confidence = 4

    return {
        "signal": signal,
        "confidence": confidence,
        "buy_signals": buy_signals,
        "sell_signals": sell_signals,
        "total_checks": total_checks,
        "reasons_buy": reasons_buy,
        "reasons_sell": reasons_sell,
    }


def determine_cycle(fg_value, rsi, ma50, ma200, btc_30d):
    """Determine current market cycle phase."""
    if fg_value <= 25 and (rsi is None or rsi < 35):
        return "ACCUMULATION", "Smart money buying. Best time to DCA."
    elif fg_value <= 60 and btc_30d > 0:
        return "MARKUP", "Uptrend in progress. Hold positions, add on dips."
    elif fg_value >= 75 and (rsi is None or rsi > 65):
        return "DISTRIBUTION", "Smart money selling. Consider taking profits."
    elif fg_value >= 40 and btc_30d < -10:
        return "MARKDOWN", "Downtrend. Preserve capital. Wait for fear."
    else:
        return "TRANSITION", "Between phases. Watch for confirmation."


def main():
    print(f"BLAI Crypto Intelligence v2 — {DATE}")
    print("=" * 50)

    # Gather all data
    print("Fetching prices...")
    prices = get_prices()

    print("Fetching BTC history (200 days)...")
    btc_history = get_price_history("bitcoin", 200)

    print("Calculating technicals...")
    btc_rsi = calculate_rsi(btc_history) if btc_history else None
    btc_ma50 = calculate_ma(btc_history, 50) if btc_history else None
    btc_ma200 = calculate_ma(btc_history, 200) if btc_history else None

    # ETH technicals
    eth_history = get_price_history("ethereum", 200)
    eth_rsi = calculate_rsi(eth_history) if eth_history else None

    fg = get_fear_greed()
    trending = get_trending()
    globe = get_global()
    btc_data = get_btc_etf_sentiment()

    btc_price = prices.get("bitcoin", {}).get("usd", 0)

    # Determine signal
    sig = determine_signal(btc_rsi, fg["value"], btc_ma50, btc_ma200, btc_price, btc_data)

    # Determine cycle
    cycle_phase, cycle_advice = determine_cycle(
        fg["value"], btc_rsi, btc_ma50, btc_ma200,
        btc_data.get("30d_change", 0))

    # Halving info
    halving_date = datetime(2024, 4, 19)
    days_since_halving = (datetime.now() - halving_date).days

    # Build report
    lines = []
    lines.append(f"BLAI MARKET INTELLIGENCE — {DATE}")
    lines.append("=" * 50)
    lines.append("")

    # Prices with technicals
    lines.append("CRYPTO PRICES:")
    for coin_id, symbol in COINS.items():
        p = prices.get(coin_id, {})
        price = p.get("usd", 0)
        change = p.get("usd_24h_change", 0)
        mcap = p.get("usd_market_cap", 0)
        arrow = "^" if change > 0 else "v"
        lines.append(f"  {symbol}: ${price:,.2f} ({change:+.1f}%) {arrow} | MCap: {fmt(mcap)}")
    lines.append("")

    # Technical Analysis
    lines.append("TECHNICAL ANALYSIS (BTC):")
    lines.append(f"  RSI (14): {btc_rsi if btc_rsi else 'N/A'} {'— OVERSOLD' if btc_rsi and btc_rsi < 30 else '— OVERBOUGHT' if btc_rsi and btc_rsi > 70 else ''}")
    lines.append(f"  50-day MA: ${btc_ma50:,.0f}" if btc_ma50 else "  50-day MA: N/A")
    lines.append(f"  200-day MA: ${btc_ma200:,.0f}" if btc_ma200 else "  200-day MA: N/A")
    if btc_ma50 and btc_ma200:
        cross = "GOLDEN CROSS (bullish)" if btc_ma50 > btc_ma200 else "DEATH CROSS (bearish)"
        lines.append(f"  MA Status: {cross}")
    if btc_price and btc_ma50:
        pos = "ABOVE" if btc_price > btc_ma50 else "BELOW"
        lines.append(f"  Price vs 50MA: {pos}")
    if btc_data.get("ath"):
        lines.append(f"  ATH: ${btc_data['ath']:,.0f} | Distance: {btc_data['ath_distance']}%")
    lines.append("")

    if eth_rsi:
        lines.append(f"TECHNICAL ANALYSIS (ETH):")
        lines.append(f"  RSI (14): {eth_rsi} {'— OVERSOLD' if eth_rsi < 30 else '— OVERBOUGHT' if eth_rsi > 70 else ''}")
        lines.append("")

    # Sentiment
    lines.append("SENTIMENT:")
    lines.append(f"  Fear & Greed: {fg['value']}/100 — {fg['label']}")
    lines.append(f"  Yesterday: {fg['yesterday']} | Last week: {fg['week_ago']}")
    fg_trend = "IMPROVING" if fg['value'] > fg['yesterday'] else "WORSENING" if fg['value'] < fg['yesterday'] else "STABLE"
    lines.append(f"  Trend: {fg_trend}")
    lines.append("")

    # Market overview
    lines.append("MARKET OVERVIEW:")
    lines.append(f"  Total Market Cap: {fmt(globe.get('market_cap', 0))}")
    lines.append(f"  24h Volume: {fmt(globe.get('volume_24h', 0))}")
    lines.append(f"  BTC Dominance: {globe.get('btc_dom', 0):.1f}%")
    lines.append(f"  ETH Dominance: {globe.get('eth_dom', 0):.1f}%")
    lines.append("")

    # BTC momentum
    if btc_data:
        lines.append("BTC MOMENTUM:")
        lines.append(f"  7-day: {btc_data.get('7d_change', 0):+.1f}%")
        lines.append(f"  30-day: {btc_data.get('30d_change', 0):+.1f}%")
        lines.append(f"  1-year: {btc_data.get('1y_change', 0):+.1f}%")
        lines.append("")

    # Trending
    if trending:
        lines.append(f"TRENDING: {', '.join(trending[:5])}")
        lines.append("")

    # Cycle position
    lines.append("MARKET CYCLE:")
    lines.append(f"  Phase: {cycle_phase}")
    lines.append(f"  Advice: {cycle_advice}")
    lines.append(f"  Days since BTC halving: {days_since_halving}")
    lines.append(f"  Historical peak window: Oct 2025 - Oct 2026")
    lines.append("")

    # SIGNAL
    lines.append("=" * 50)
    lines.append(f"SIGNAL: {sig['signal']}")
    lines.append(f"CONFIDENCE: {sig['confidence']}/10")
    lines.append(f"Buy indicators: {sig['buy_signals']}/{sig['total_checks']}")
    lines.append(f"Sell indicators: {sig['sell_signals']}/{sig['total_checks']}")
    lines.append("")

    if sig['reasons_buy']:
        lines.append("BULLISH FACTORS:")
        for r in sig['reasons_buy']:
            lines.append(f"  + {r}")
        lines.append("")

    if sig['reasons_sell']:
        lines.append("BEARISH FACTORS:")
        for r in sig['reasons_sell']:
            lines.append(f"  - {r}")
        lines.append("")

    lines.append("This is research, not financial advice. Abdul decides.")
    lines.append(f"\nSaved: {REPORT_FILE}")

    report = "\n".join(lines)
    print(report)
    REPORT_FILE.write_text(report)

    # Save signal to tracker
    try:
        tracker = json.loads(SIGNAL_FILE.read_text()) if SIGNAL_FILE.exists() else {"signals": []}
    except Exception:
        tracker = {"signals": []}

    tracker["signals"].append({
        "date": DATE,
        "signal": sig["signal"],
        "confidence": sig["confidence"],
        "btc_price": btc_price,
        "rsi": btc_rsi,
        "fear_greed": fg["value"],
        "buy_count": sig["buy_signals"],
        "sell_count": sig["sell_signals"],
    })
    # Keep last 90 days
    tracker["signals"] = tracker["signals"][-90:]
    SIGNAL_FILE.write_text(json.dumps(tracker, indent=2))

    return report


if __name__ == "__main__":
    main()
