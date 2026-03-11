---
description: Phase 3 - Build the core backtest engine (broker, portfolio, engine loop)
---

# Phase 3: Backtest Engine Core

// turbo-all

## Prerequisites
- Phase 1 & 2 must be completed

## Steps

1. Create `src/backtest/engine/broker.py`:
   - `SimulatedBroker` class:
     - `__init__(self, commission_rate: float = 0.001, slippage_rate: float = 0.0005)`
     - `process_orders(orders: list[Order], current_candle: Candle) -> list[Fill]`:
       - MARKET orders: fill at current candle's open price + slippage
       - LIMIT BUY orders: fill if candle low <= limit price
       - LIMIT SELL orders: fill if candle high >= limit price
       - Calculate commission as `fill_price * size * commission_rate`
     - Keep an `order_history` and `fill_history` for auditing

2. Create `src/backtest/engine/portfolio.py`:
   - `Portfolio` class:
     - `__init__(self, initial_capital: float)`
     - Properties: `cash`, `equity`, `positions: dict[str, Position]`, `trades: list[Trade]`, `snapshots: list[PortfolioSnapshot]`
     - `update_on_fill(fill: Fill)`:
       - If opening new position: deduct cash, create Position
       - If closing existing position: add cash, create Trade with realized PnL
       - Handle partial fills (reduce position size)
     - `mark_to_market(symbol: str, current_price: float)` — update unrealized PnL
     - `snapshot(timestamp: datetime)` — record current state to snapshots list
     - `get_position(symbol: str) -> Position | None`
     - `total_equity` property = cash + sum of position values

3. Create `src/backtest/engine/engine.py`:
   - `BacktestEngine` class:
     - `__init__(self, data_provider, strategy, broker, portfolio)`
     - `run() -> BacktestResult`:
       1. Call `strategy.on_init()`
       2. For each candle from data_provider:
          a. Mark all positions to market with candle.close
          b. Call `orders = strategy.on_candle(candle, portfolio)`
          c. `fills = broker.process_orders(orders, candle)`
          d. For each fill: `portfolio.update_on_fill(fill)`
          e. `portfolio.snapshot(candle.timestamp)`
       3. Call `strategy.on_stop()`
       4. Return `BacktestResult` with portfolio snapshots, trades, fills
   - `BacktestResult` dataclass: snapshots, trades, fills, start_time, end_time

4. Verify:
   - Create a quick test script that uses a dummy strategy (buy on first bar, sell on last bar)
   - Run: `uv run python -c "..."` to confirm engine runs end-to-end without errors
   - Print final equity and number of trades
