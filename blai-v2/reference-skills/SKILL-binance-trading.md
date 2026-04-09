# SKILL: Binance Trading Operations

## Purpose
Execute Binance trading ops: spot, futures, bots, API automation, risk management.

---

## Account Types
- **Spot**: Buy/sell at market price, no leverage, safest
- **Futures**: Leverage 1x-125x, high risk/reward
- **Margin**: Borrowed funds for leveraged spot
- **Earn**: Staking, savings, liquidity farming

## Order Types
- **Market**: Immediate at current price
- **Limit**: At your set price
- **Stop-Limit**: Triggers limit order at a price level
- **OCO**: Take-profit + stop-loss combo
- **Trailing Stop**: Stop-loss follows price up

## Candlestick Timeframes
- Day trading: 5m, 15m, 1h
- Swing trading: 4h, 1D
- Investing: 1D, 1W

---

## Trading Bots (Binance Built-in)
- **Spot Grid**: Auto buy low / sell high in a range. Best for sideways markets. Expected 1-5%/week.
- **DCA Bot**: Buys at regular intervals, averages entry price. Best for downtrend accumulation.
- **Futures Grid**: Grid + leverage. HIGH RISK. Max 2-3x, only after mastering spot grid.
- **Rebalancing Bot**: Maintains target portfolio allocations.

---

## Binance API
- Keys: Account > API Management. Enable Reading + Spot Trading only. NEVER enable Withdrawals. Restrict to server IP.
- Store keys in `~/.bashrc` as `BINANCE_API_KEY` and `BINANCE_API_SECRET`
- Library: `python-binance` (`pip install python-binance`)
- Client: `from binance.client import Client`
- Key methods: `get_account()`, `get_symbol_ticker()`, `create_order()`, `get_recent_trades()`, `get_klines()`
- Grid bot script: `~/scripts/grid-bot.py` — args: SYMBOL LOWER UPPER GRIDS INVESTMENT
- DCA bot script: `~/scripts/dca-bot.py` — cron: `0 9 * * *` — args: SYMBOL USDT_AMOUNT

---

## Binance Earn
- **Flexible**: 1-5% APR (BTC/ETH), 5-15% (stablecoins), withdraw anytime
- **Locked Staking**: 3-20% APR, 30-120 day lock
- **Launchpool**: Stake BNB to farm new tokens, 5-30% APR short-term

---

## Risk Management — 5 Golden Rules
1. Never risk >2% of account per trade
2. Every trade MUST have a stop-loss before entry
3. Minimum 1:2 risk-reward ratio
4. After 2 consecutive losses, stop for the day
5. Log every trade: entry, exit, reason, result

Position Size = (Account Balance x Risk%) / Stop-Loss Distance%

Leverage guide: None (beginner) → 2-3x (3+ months) → 5x (6+ months) → 10x+ (expert only)

---

## Rules for BLAI
- NEVER execute any trade without Boss's explicit approval
- ALWAYS explain risk before recommending any trade
- Start with SPOT only — no futures until Boss says so
- Paper trade before real money
- Track all recommendations and outcomes
- If unsure about market direction, say so
- Report market conditions every morning automatically
