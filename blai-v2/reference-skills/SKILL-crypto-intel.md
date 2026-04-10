# SKILL: Crypto Intelligence (REAL data, no fabrication)

This is the executable replacement for the older markdown-only crypto
research and binance-trading docs. It pulls REAL data from public APIs
and gives Boss research-grade signals. NO guarantees, NO 100% claims,
NO auto-trading.

## Functions (all in `skills/crypto_intel.py`)

### Market data (real, live)
- `get_market_snapshot()` — BTC/ETH/SOL/BNB price, 24h change, market cap,
  BTC dominance, F&G index. From CoinGecko + alternative.me.
- `get_ohlc(coin_id, days)` — Real historical candles from CoinGecko.
- `compute_indicators(ohlc)` — Real RSI(14), SMA(10), SMA(20), period
  high/low, position vs SMA. Math, not opinion.

### Sentiment / positioning
- `get_funding_rate(symbol="BTC-USDT-SWAP")` — Real OKX perpetual funding
  (Binance is geo-blocked from this VM, OKX is the live proxy).
  Negative funding = shorts paying longs (contrarian-bullish).
  Very positive funding = longs over-leveraged (local top warning).
- `get_etf_flows()` — Daily BTC spot ETF net flows, scraped from Farside.
  This is the SINGLE BEST medium-term signal — real institutional money.

### Macro
- `get_macro_context()` — DXY, S&P 500, gold from Yahoo Finance free API.
  Crypto doesn't trade in a vacuum.

### Guru pulse (REAL public sources, never paraphrased)
- `get_saylor_pulse()` — SEC EDGAR. Every MicroStrategy BTC purchase
  requires an 8-K filing within 4 business days, with the exact BTC count
  and average price. This is more reliable than any tweet because it's
  a federal filing.
- `get_hayes_essays()` — Arthur Hayes Substack RSS, real titles + links.
- `get_raoul_pal_pulse()` — RealVision RSS.

### Synthesis
- `detect_setups()` — Combines F&G + funding + ETF flows into a tagged
  setup with REAL confidence percentage (capped at 80% — never claims
  certainty). Returns the bias, the factors, and a warning that this
  is research not a guarantee.
- `get_full_briefing()` — One-shot human-readable briefing for WhatsApp.
- `get_guru_pulse()` — Human-readable guru briefing.

### Trade math
- `position_size(account_usd, risk_pct, entry, stop)` — Pure calculator.
  Returns position size in units + USD, max loss, leverage implied,
  and rule_check (refuses risk_pct > 5%, warns if > 2%).

### Track record
- `log_signal(symbol, direction, entry, target, stop, confidence_pct, reason)`
  Saves to memory/crypto_signals.json with timestamp + R/R.
- `get_signal_scorecard()` — Real hit rate from closed signals. If BLAI's
  hit rate is 45%, the dashboard says 45%. Honesty is the moat.

## ABSOLUTE rules (non-negotiable, also in preferences.json)

1. **NEVER promise guaranteed profit.** No "100%", no "risk-free", no
   "can't lose", no "sure thing". These words make BLAI useless the
   first time it's wrong, and it WILL be wrong sometimes.
2. **Confidence is capped at 80%.** Even when every single indicator
   aligns, the future is uncertain.
3. **NEVER auto-trade.** BLAI calculates position size and gives
   entry/stop/target. The user clicks the buttons on Binance themselves.
4. **Quote gurus VERBATIM.** Use the actual title from Substack RSS or
   the actual filing date from SEC EDGAR. Never paraphrase a Saylor
   quote — that's how disinformation starts.
5. **Every signal MUST be logged.** Use log_signal() so BLAI's real
   hit rate is measurable over time.
6. **Always include a stop-loss.** Position sizing requires a stop.
   Refuse to compute size without one.
7. **2% per-trade rule.** position_size() warns above 2% account risk
   and refuses above 5%.

## What BLAI tells the user when asked about crypto

When Boss says "should I buy BTC?", BLAI does NOT say "yes" or "no".
BLAI runs `get_full_briefing()`, then `detect_setups()`, then says
something like:

> Current setup: MILD LONG, confidence 60%.
> Factors:
>   - Fear & Greed at 18 (Extreme Fear) — contrarian-bullish
>   - Funding rate -0.008% (shorts paying longs)
>   - ETF 5d net flow +$842M (institutional buying)
> Suggested risk: 1.5% of account
> Stop suggestion: <calculated from recent swing low>
> R/R target: 1:3
> This is research, not a guarantee. You make the trade decision.

That is the entire job. BLAI is a research analyst, not a fortune teller.

## What requires Boss action (one-time)

- **Whale Alert API key** (free at whale-alert.io): if added to
  config/api_keys.json under `whale_alert`, BLAI can also pull real
  $1M+ on-chain transfers. Optional.
- **Glassnode free API key**: similar — adds reserve/whale on-chain
  metrics. Optional.

## What BLAI cannot do from this VM

- Direct Binance API access (geo-blocked HTTP 451 from GCP US-Central).
  Workaround: OKX as the funding-rate proxy + CoinGecko for prices.
- Bybit API (also blocked).
- Twitter/X scraping (Nitter is dead, Twitter killed public mirrors).
  Workaround: SEC EDGAR for Saylor + Substack RSS for Hayes.
