"""Starter paper-trading bot template.

This script demonstrates, end to end:
1. Downloading historical daily price data with yfinance
2. Calculating two moving averages (short and long)
3. Generating BUY/SELL signals when averages cross
4. Simulating trades with virtual cash (paper trading)
5. Printing a compact performance summary
"""

from __future__ import annotations

import argparse
import dataclasses
from typing import List

import pandas as pd
import yfinance as yf


@dataclasses.dataclass
class Trade:
    side: str
    date: pd.Timestamp
    price: float
    quantity: int


@dataclasses.dataclass
class BacktestResult:
    starting_cash: float
    ending_equity: float
    open_quantity: int
    trades: List[Trade]


def fetch_data(symbol: str, start: str, end: str) -> pd.DataFrame:
    """Fetch historical OHLCV data for a ticker symbol."""
    data = yf.download(symbol, start=start, end=end, auto_adjust=True, progress=False)
    if data.empty:
        raise ValueError("No market data returned. Check symbol/date range.")
    return data


def apply_indicators(data: pd.DataFrame, short_window: int, long_window: int) -> pd.DataFrame:
    """Add moving-average columns used by the strategy."""
    if short_window >= long_window:
        raise ValueError("short_window must be smaller than long_window.")

    result = data.copy()
    result["ma_short"] = result["Close"].rolling(short_window).mean()
    result["ma_long"] = result["Close"].rolling(long_window).mean()
    return result.dropna().copy()


def run_paper_backtest(data: pd.DataFrame, initial_cash: float) -> BacktestResult:
    """Simulate a long-only crossover strategy with virtual cash."""
    cash = initial_cash
    quantity = 0
    trades: List[Trade] = []

    for i in range(1, len(data)):
        today = data.iloc[i]
        yesterday = data.iloc[i - 1]

        cross_up = today["ma_short"] > today["ma_long"] and yesterday["ma_short"] <= yesterday["ma_long"]
        cross_down = today["ma_short"] < today["ma_long"] and yesterday["ma_short"] >= yesterday["ma_long"]

        price = float(today["Close"])
        date = data.index[i]

        if cross_up and quantity == 0:
            quantity = int(cash // price)
            if quantity > 0:
                cash -= quantity * price
                trades.append(Trade(side="BUY", date=date, price=price, quantity=quantity))

        elif cross_down and quantity > 0:
            cash += quantity * price
            trades.append(Trade(side="SELL", date=date, price=price, quantity=quantity))
            quantity = 0

    final_price = float(data["Close"].iloc[-1])
    equity = cash + quantity * final_price
    return BacktestResult(
        starting_cash=initial_cash,
        ending_equity=equity,
        open_quantity=quantity,
        trades=trades,
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Simple paper-trading backtest using MA crossovers.")
    parser.add_argument("--symbol", default="SPY", help="Ticker symbol (default: SPY)")
    parser.add_argument("--start", default="2020-01-01", help="Start date YYYY-MM-DD")
    parser.add_argument("--end", default="2024-01-01", help="End date YYYY-MM-DD")
    parser.add_argument("--short-window", type=int, default=10, help="Short MA window (default: 10)")
    parser.add_argument("--long-window", type=int, default=50, help="Long MA window (default: 50)")
    parser.add_argument("--cash", type=float, default=10_000.0, help="Starting paper cash (default: 10000)")
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    dataset = fetch_data(args.symbol, start=args.start, end=args.end)
    enriched = apply_indicators(dataset, short_window=args.short_window, long_window=args.long_window)
    result = run_paper_backtest(enriched, initial_cash=args.cash)

    pnl = result.ending_equity - result.starting_cash
    pnl_pct = (pnl / result.starting_cash) * 100

    print("== Paper Backtest Summary ==")
    print(f"Symbol: {args.symbol}")
    print(f"Date range: {args.start} -> {args.end}")
    print(f"Strategy: MA{args.short_window} / MA{args.long_window} crossover")
    print(f"Trades executed: {len(result.trades)}")
    print(f"Open shares at end: {result.open_quantity}")
    print(f"Starting cash: ${result.starting_cash:,.2f}")
    print(f"Ending equity: ${result.ending_equity:,.2f}")
    print(f"P/L: ${pnl:,.2f} ({pnl_pct:.2f}%)")

    if result.trades:
        print("\nFirst 5 trades:")
        for trade in result.trades[:5]:
            print(f"{trade.date.date()} | {trade.side:<4} {trade.quantity:>4} @ ${trade.price:,.2f}")


if __name__ == "__main__":
    main()
