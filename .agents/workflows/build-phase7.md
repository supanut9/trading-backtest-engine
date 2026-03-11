---
description: Phase 7 - Write comprehensive tests and run full verification
---

# Phase 7: Tests & Verification

// turbo-all

## Prerequisites
- Phase 1-6 must be completed

## Steps

1. Create `tests/conftest.py`:
   - Shared fixtures:
     - `sample_candles` — list of 100 Candle objects with known values
     - `sample_df` — DataFrame from sample CSV
     - `sample_data_provider` — DataProvider from sample data
     - `sample_portfolio` — Portfolio with 10000 initial capital
     - `sample_broker` — SimulatedBroker with default settings

2. Create `tests/test_models.py`:
   - Test Candle creation and field access
   - Test Order creation with different types and sides
   - Test Position.mark_to_market() with known prices
   - Test Trade PnL calculation
   - Test PortfolioSnapshot creation

3. Create `tests/test_loader.py`:
   - Test load_csv with sample data file
   - Test column validation (missing column raises ValueError)
   - Test date parsing and sorting
   - Test load_data auto-detection

4. Create `tests/test_broker.py`:
   - Test market order fills at open price + slippage
   - Test limit buy fills when price touches limit
   - Test limit sell fills when price touches limit
   - Test commission calculation
   - Test order that should NOT fill (limit not reached)

5. Create `tests/test_engine.py`:
   - Test engine runs end-to-end with a simple always-buy-first-bar strategy
   - Test that snapshots are recorded each bar
   - Test that final equity equals initial_capital + PnL from trades
   - Test with empty data (should not crash)

6. Create `tests/test_metrics.py`:
   - Test total_return with known equity curve
   - Test max_drawdown with known peak/trough
   - Test sharpe_ratio with known returns series
   - Test win_rate edge cases (0 trades, all wins, all losses)

7. Create `tests/test_sma_cross.py`:
   - Test that SMA cross generates no orders before warmup period
   - Test that crossover detection works correctly
   - Test full backtest produces expected number of trades on sample data

8. Run all tests:
   ```bash
   uv run pytest tests/ -v --tb=short
   ```

9. Run with coverage:
   ```bash
   uv run pytest tests/ -v --cov=backtest --cov-report=term-missing
   ```

10. Final end-to-end verification:
    ```bash
    uv run backtest run
    uv run backtest run --strategy rsi_mean_revert
    uv run backtest list-strategies
    ```
    - Confirm both strategies produce valid output
    - Confirm HTML reports are generated in `reports/`
