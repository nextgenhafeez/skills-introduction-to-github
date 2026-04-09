#!/usr/bin/env python3
"""
Market Intelligence + Rich Brain
Tracks crypto, institutional moves, and rich people decisions.
"""

import json
import time
import requests
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.brain import think_simple
from pathlib import Path

MEMORY_DIR = Path(__file__).parent.parent / "memory"


def get_crypto_prices() -> dict:
    """Get current BTC, ETH, SOL prices from CoinGecko (free, no key)."""
    try:
        resp = requests.get(
            "https://api.coingecko.com/api/v3/simple/price",
            params={"ids": "bitcoin,ethereum,solana,binancecoin", "vs_currencies": "usd", "include_24hr_change": "true"},
            timeout=10
        )
        if resp.status_code == 200:
            return resp.json()
    except:
        pass
    return {}


def get_fear_greed() -> dict:
    """Get Fear & Greed Index."""
    try:
        resp = requests.get("https://api.alternative.me/fng/?limit=1", timeout=10)
        if resp.status_code == 200:
            data = resp.json()["data"][0]
            return {"value": int(data["value"]), "label": data["value_classification"]}
    except:
        pass
    return {"value": 0, "label": "unknown"}


def generate_morning_brief() -> str:
    """Generate morning market brief for WhatsApp."""
    prices = get_crypto_prices()
    fng = get_fear_greed()

    btc = prices.get("bitcoin", {})
    eth = prices.get("ethereum", {})
    sol = prices.get("solana", {})

    btc_price = btc.get("usd", 0)
    btc_change = btc.get("usd_24h_change", 0)
    eth_price = eth.get("usd", 0)
    eth_change = eth.get("usd_24h_change", 0)
    sol_price = sol.get("usd", 0)
    sol_change = sol.get("usd_24h_change", 0)

    # Determine signal based on Fear & Greed + price action
    signal = "HOLD"
    if fng["value"] < 20 and btc_change < -3:
        signal = "WATCH FOR BUY (extreme fear + dip)"
    elif fng["value"] > 80 and btc_change > 5:
        signal = "TAKE PROFIT (extreme greed)"
    elif fng["value"] < 30:
        signal = "ACCUMULATE SLOWLY (fear zone)"

    brief = f"""MARKET BRIEF — {time.strftime('%b %d')}

BTC: ${btc_price:,.0f} ({btc_change:+.1f}%)
ETH: ${eth_price:,.0f} ({eth_change:+.1f}%)
SOL: ${sol_price:,.0f} ({sol_change:+.1f}%)
Fear & Greed: {fng['value']}/100 ({fng['label']})

Signal: {signal}"""

    # Save to memory
    MEMORY_DIR.mkdir(parents=True, exist_ok=True)
    signals_file = MEMORY_DIR / "signals.json"
    signals = []
    if signals_file.exists():
        signals = json.loads(signals_file.read_text())
    signals.append({
        "date": time.strftime("%Y-%m-%d"),
        "btc_price": btc_price,
        "fng": fng["value"],
        "signal": signal
    })
    signals_file.write_text(json.dumps(signals[-90:], indent=2))  # Keep 90 days

    return brief


def generate_rich_brain_analysis() -> str:
    """Use AI to analyze institutional moves and rich people strategies."""
    prices = get_crypto_prices()
    fng = get_fear_greed()

    btc_price = prices.get("bitcoin", {}).get("usd", 0)

    prompt = f"""You are a market intelligence analyst. Today's data:
- BTC: ${btc_price:,.0f}
- Fear & Greed: {fng['value']}/100 ({fng['label']})
- Date: {time.strftime('%Y-%m-%d')}

Based on the principles of:
- Rothschild: "Buy when there's blood in the streets"
- Buffett: "Be greedy when others are fearful"
- Ray Dalio: "Follow the debt cycle, diversify"
- BlackRock: Track institutional ETF flows
- Saylor: Long-term BTC conviction

Give a 5-line market assessment. What would these investors likely do today? Be specific, not generic. End with a clear BUY/SELL/HOLD recommendation with confidence level."""

    analysis = think_simple(prompt)
    return analysis or "Rich brain analysis unavailable — API limit reached."


if __name__ == "__main__":
    print(generate_morning_brief())
    print("\n---\n")
    print(generate_rich_brain_analysis())
