---
description: Phase 4 - Build strategy framework with base class and example strategies
---

# Phase 4: Strategy Framework & Built-in Strategies

// turbo-all

## Prerequisites
- Phase 1, 2, 3 must be completed

## Steps

1. Create `src/backtest/strategy/base.py`:
   - `AbstractStrategy` (ABC):
     - `name: str` abstract property
     - `on_init(self) -> None` — called once before backtest starts, use for indicator warmup tracking
     - `on_candle(self, candle: Candle, portfolio: Portfolio) -> list[Order]` — abstract, must return list of orders (can be empty)
     - `on_stop(self) -> None` — called after backtest ends, optional cleanup
     - Helper method: `_create_market_order(symbol, side, size) -> Order`
     - Helper method: `_create_limit_order(symbol, side, size, price) -> Order`

2. Create `src/backtest/strategy/sma_cross.py`:
   - `SmaCrossStrategy(AbstractStrategy)`:
     - Params: `symbol: str`, `fast_period: int = 10`, `slow_period: int = 30`, `position_size: float = 1.0`
     - On init: create empty price history list
     - On candle:
       - Append close price to history
       - If not enough data for slow SMA, return empty
       - Calculate fast SMA and slow SMA from price history
       - If fast crosses above slow AND no position: BUY market order
       - If fast crosses below slow AND has position: SELL market order
     - Track previous SMA values to detect crossover (not just comparison)

3. Create `src/backtest/strategy/rsi_mean_revert.py`:
   - `RsiMeanRevertStrategy(AbstractStrategy)`:
     - Params: `symbol: str`, `rsi_period: int = 14`, `oversold: float = 30`, `overbought: float = 70`, `position_size: float = 1.0`
     - Implement RSI calculation from price history (Wilder's smoothing)
     - If RSI < oversold AND no position: BUY
     - If RSI > overbought AND has position: SELL

4. Verify:
   - Run SMA cross strategy on sample BTC data through the engine
   - Print number of trades, final equity
   - Confirm it generates reasonable trades (not 0, not every bar)
   - Run: `uv run python -c "from backtest.engine.engine import BacktestEngine; ..."`
