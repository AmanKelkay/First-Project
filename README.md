# First-Project

A starter project that shows how a paper-trading bot works using historical market data.

## Files

- `index.html` — visual guide explaining the paper-trading workflow.
- `trading_bot_starter.py` — runnable backtest script with simulated trades.

## Quick start

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install yfinance pandas
python3 trading_bot_starter.py
```

## How it works

When you run `trading_bot_starter.py`, it performs these steps:

1. **Download data**
   - Fetches daily historical prices from Yahoo Finance via `yfinance`.
2. **Compute indicators**
   - Adds a short and long moving average (`ma_short`, `ma_long`).
3. **Create signals**
   - **Buy** when the short MA crosses above the long MA.
   - **Sell** when the short MA crosses below the long MA.
4. **Simulate orders**
   - Uses virtual cash only (paper trading).
   - Buys as many whole shares as possible on a buy signal.
   - Sells all shares on a sell signal.
5. **Report results**
   - Prints trade count, ending equity, profit/loss, and sample trades.

## Example command options

```bash
python3 trading_bot_starter.py \
  --symbol AAPL \
  --start 2019-01-01 \
  --end 2024-01-01 \
  --short-window 20 \
  --long-window 100 \
  --cash 25000
```

## Notes

- Educational simulation only; not financial advice.
- Real trading requires slippage, fees, risk limits, and robust error handling.
