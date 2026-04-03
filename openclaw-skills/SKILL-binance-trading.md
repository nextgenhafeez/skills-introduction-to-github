# SKILL: Binance Trading Operations

## Purpose
Understand Binance exchange inside-out — how to trade spot, futures, use trading bots, read charts, manage risk, and eventually automate trades via Binance API. This is an EXECUTION skill.

---

## PART 1: BINANCE BASICS

### Account Types
- **Spot Account**: Buy and sell crypto at current market price. No leverage. Safest.
- **Futures Account**: Trade contracts with leverage (1x-125x). Higher risk/reward.
- **Margin Account**: Borrow funds to trade spot with leverage. Medium risk.
- **Earn Account**: Staking, savings, liquidity farming. Passive income.

### Order Types (Must Know All)
| Order Type | What It Does | When to Use |
|-----------|-------------|-------------|
| **Market Order** | Buy/sell immediately at current price | When speed matters more than price |
| **Limit Order** | Buy/sell at a specific price you set | When you want a better price and can wait |
| **Stop-Limit** | Triggers a limit order when price hits a level | For stop-losses and breakout entries |
| **OCO (One-Cancels-Other)** | Sets both take-profit and stop-loss | For managing open positions |
| **Trailing Stop** | Stop-loss that follows price up | For locking in profits as price rises |

### Reading a Candlestick Chart
```
Green candle = price went UP in that period
Red candle = price went DOWN in that period

  │  ← Upper wick (high)
  █  ← Body (open to close)
  █
  │  ← Lower wick (low)

Timeframes: 1m, 5m, 15m, 1h, 4h, 1D, 1W
- Day trading: Use 5m, 15m, 1h
- Swing trading: Use 4h, 1D
- Investing: Use 1D, 1W
```

---

## PART 2: HOW TO TRADE ON BINANCE (Step by Step)

### Spot Trading
```
1. Go to Trade > Spot
2. Select trading pair (e.g., BTC/USDT)
3. Choose order type (Limit recommended for beginners)
4. Enter price and amount
5. Click "Buy BTC" or "Sell BTC"
6. Order appears in "Open Orders" until filled
```

### Futures Trading (CAUTION — CAN LOSE ALL FUNDS)
```
1. Transfer USDT from Spot to Futures wallet
2. Go to Derivatives > USDT-M Futures
3. Select pair (e.g., BTCUSDT)
4. Choose leverage (START WITH 2x-3x MAX)
5. Choose Long (bet price goes up) or Short (bet price goes down)
6. Set entry price (limit order)
7. ALWAYS set Stop-Loss and Take-Profit BEFORE entering
8. Monitor position in "Positions" tab
```

### Risk per Trade Calculator
```
Account size: $1,000
Risk per trade: 2% = $20
Stop-loss distance: 3%
Position size = $20 / 0.03 = $666

This means: risk $20 to potentially make $40-$60 (2:1 or 3:1 reward)
```

---

## PART 3: BINANCE BUILT-IN TRADING BOTS

### Spot Grid Bot
- **What**: Automatically buys low and sells high within a price range
- **Best for**: Sideways/ranging markets
- **Setup**:
  1. Go to Trade > Trading Bots > Spot Grid
  2. Select pair (e.g., BTC/USDT)
  3. Set price range (lower price – upper price)
  4. Set number of grids (more grids = more trades, smaller profit each)
  5. Set investment amount
  6. Click Create
- **Example**: BTC range $60,000–$70,000, 20 grids, $500 invested
- **Expected return**: 1-5% per week in sideways market

### DCA Bot
- **What**: Buys at regular intervals, averaging your entry price
- **Best for**: Accumulating during downtrends
- **Setup**:
  1. Trading Bots > DCA
  2. Select coin and frequency (daily, weekly)
  3. Set buy amount per interval
  4. Set optional take-profit target
- **Expected return**: Market average over time

### Futures Grid Bot
- **What**: Grid trading with leverage on futures
- **Risk**: HIGH — can be liquidated
- **Only use**: With 2x-3x leverage max, and only after mastering spot grid

### Rebalancing Bot
- **What**: Keeps your portfolio at target allocations (e.g., 50% BTC, 30% ETH, 20% SOL)
- **Best for**: Long-term holders who want automatic rebalancing

---

## PART 4: BINANCE API (For Automation)

### Getting API Keys
1. Go to Binance > Account > API Management
2. Create new API key
3. Set permissions: "Enable Reading" + "Enable Spot Trading"
4. NEVER enable "Enable Withdrawals" on bot keys
5. Restrict to your server IP address

### Store Keys on VM
```bash
echo 'export BINANCE_API_KEY="your_key"' >> ~/.bashrc
echo 'export BINANCE_API_SECRET="your_secret"' >> ~/.bashrc
source ~/.bashrc
```

### Python Setup
```bash
pip install python-binance
```

### Basic Operations
```python
from binance.client import Client
import os

client = Client(
    os.environ['BINANCE_API_KEY'],
    os.environ['BINANCE_API_SECRET']
)

# Check account balance
balances = client.get_account()['balances']
for b in balances:
    if float(b['free']) > 0:
        print(f"{b['asset']}: {b['free']}")

# Get current BTC price
price = client.get_symbol_ticker(symbol="BTCUSDT")
print(f"BTC Price: ${price['price']}")

# Place a limit buy order
order = client.create_order(
    symbol='BTCUSDT',
    side='BUY',
    type='LIMIT',
    timeInForce='GTC',
    quantity=0.001,
    price='60000'
)

# Place a market sell order
order = client.create_order(
    symbol='BTCUSDT',
    side='SELL',
    type='MARKET',
    quantity=0.001
)

# Get recent trades
trades = client.get_recent_trades(symbol='BTCUSDT', limit=5)

# Get candlestick data (for analysis)
candles = client.get_klines(
    symbol='BTCUSDT',
    interval=Client.KLINE_INTERVAL_1HOUR,
    limit=100
)
```

### Simple Grid Bot Script
```python
#!/usr/bin/env python3
"""
Simple Binance Spot Grid Bot
Usage: python3 grid-bot.py BTCUSDT 60000 70000 10 500
"""
import sys
import time
from binance.client import Client
import os

client = Client(os.environ['BINANCE_API_KEY'], os.environ['BINANCE_API_SECRET'])

def create_grid(symbol, lower, upper, grids, investment):
    """Create grid of buy and sell orders"""
    step = (upper - lower) / grids
    amount_per_grid = investment / grids
    
    current_price = float(client.get_symbol_ticker(symbol=symbol)['price'])
    
    orders = []
    for i in range(grids):
        grid_price = lower + (step * i)
        quantity = round(amount_per_grid / grid_price, 6)
        
        if grid_price < current_price:
            # Place buy order below current price
            order = client.create_order(
                symbol=symbol, side='BUY', type='LIMIT',
                timeInForce='GTC', quantity=quantity,
                price=str(round(grid_price, 2))
            )
            orders.append(('BUY', grid_price, order['orderId']))
            print(f"BUY  at ${grid_price:.2f} — qty: {quantity}")
        else:
            # Place sell order above current price
            order = client.create_order(
                symbol=symbol, side='SELL', type='LIMIT',
                timeInForce='GTC', quantity=quantity,
                price=str(round(grid_price, 2))
            )
            orders.append(('SELL', grid_price, order['orderId']))
            print(f"SELL at ${grid_price:.2f} — qty: {quantity}")
    
    return orders

if __name__ == "__main__":
    symbol = sys.argv[1]      # e.g., BTCUSDT
    lower = float(sys.argv[2]) # e.g., 60000
    upper = float(sys.argv[3]) # e.g., 70000
    grids = int(sys.argv[4])   # e.g., 10
    investment = float(sys.argv[5])  # e.g., 500
    
    print(f"Creating {grids} grids for {symbol} (${lower}-${upper})")
    create_grid(symbol, lower, upper, grids, investment)
    print("Grid created! Monitor on Binance app.")
```

### DCA Bot Script
```python
#!/usr/bin/env python3
"""
Simple DCA Bot — buys fixed amount at regular intervals
Run via cron: 0 9 * * * python3 ~/scripts/dca-bot.py BTCUSDT 50
"""
import sys
from binance.client import Client
import os

client = Client(os.environ['BINANCE_API_KEY'], os.environ['BINANCE_API_SECRET'])

def dca_buy(symbol, usdt_amount):
    """Market buy a fixed USDT amount of a coin"""
    price = float(client.get_symbol_ticker(symbol=symbol)['price'])
    quantity = round(usdt_amount / price, 6)
    
    order = client.create_order(
        symbol=symbol,
        side='BUY',
        type='MARKET',
        quantity=quantity
    )
    
    print(f"DCA BUY: {quantity} {symbol.replace('USDT','')} at ${price:.2f} (${usdt_amount})")
    return order

if __name__ == "__main__":
    symbol = sys.argv[1]       # e.g., BTCUSDT
    amount = float(sys.argv[2]) # e.g., 50 (USDT)
    dca_buy(symbol, amount)
```

---

## PART 5: BINANCE EARN (Passive Income)

### Simple Earn (Flexible)
- Deposit crypto, earn interest daily
- Withdraw anytime
- APR: 1-5% for BTC/ETH, 5-15% for stablecoins
- Best for: Idle funds while waiting for trades

### Locked Staking
- Lock crypto for 30/60/90/120 days
- Higher APR than flexible (3-20%)
- Can't withdraw early
- Best for: Long-term holdings

### Launchpool
- Stake BNB or other tokens to farm new token launches
- Usually 5-30% APR for short periods
- Best for: Free exposure to new projects

---

## PART 6: RISK MANAGEMENT RULES

### The 5 Golden Rules
1. **2% Rule**: Never risk more than 2% of your total account on a single trade
2. **Stop-Loss Always**: Every trade must have a stop-loss before entry
3. **Risk-Reward Minimum 1:2**: Only take trades where potential profit is 2x the risk
4. **No Revenge Trading**: After 2 consecutive losses, stop trading for the day
5. **Keep Records**: Log every trade — entry, exit, reason, result

### Position Sizing Formula
```
Position Size = (Account Balance × Risk %) / Stop-Loss Distance %

Example:
Account: $1,000
Risk: 2% = $20
Stop-loss: 5% below entry
Position: $20 / 0.05 = $400

So invest $400, with stop-loss 5% below entry = max loss $20
```

### Leverage Guide
| Experience | Max Leverage | Why |
|-----------|-------------|-----|
| Beginner | NO leverage | Learn without losing everything |
| 3+ months | 2x-3x | Small boost, manageable risk |
| 6+ months | 5x | Only on high-conviction setups |
| Expert | 10x+ | Pros only, tight stop-losses required |

---

## PART 7: WHAT TO STUDY NEXT

### Beginner (Week 1-2)
- [ ] Understand spot vs futures difference
- [ ] Place 5 practice limit orders on spot
- [ ] Learn to read candlestick charts
- [ ] Set up a Binance spot grid bot with $50-100
- [ ] Understand RSI and moving averages

### Intermediate (Week 3-4)
- [ ] Backtest a simple moving average crossover strategy
- [ ] Study support/resistance levels
- [ ] Try a DCA bot for BTC accumulation
- [ ] Learn to read the order book
- [ ] Understand funding rates

### Advanced (Month 2+)
- [ ] Set up Binance API on the VM
- [ ] Run automated DCA script via cron
- [ ] Study on-chain metrics (whale movements)
- [ ] Learn funding rate arbitrage
- [ ] Build and backtest a custom trading strategy

---

## Rules for BLAI
- NEVER execute any trade without Boss's explicit approval
- ALWAYS explain the risk before recommending any trade
- Start with SPOT only — no futures until Boss says so
- Paper trade (practice) before real money
- Track all recommendations and their outcomes
- If you're unsure about market direction, say so — don't guess
- Study Binance Academy articles daily to deepen knowledge
- Report market conditions every morning without being asked
