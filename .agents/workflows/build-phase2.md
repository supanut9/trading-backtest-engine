---
description: Phase 2 - Build data ingestion layer (CSV/Parquet loader and DataProvider)
---

# Phase 2: Data Ingestion Layer

// turbo-all

## Prerequisites
- Phase 1 must be completed (models exist)

## Steps

1. Create `src/backtest/data/loader.py`:
   - `load_csv(path: str | Path) -> pd.DataFrame` — reads OHLCV CSV, parses date column as index, validates required columns (timestamp/date, open, high, low, close, volume), sorts by date ascending
   - `load_parquet(path: str | Path) -> pd.DataFrame` — same but from parquet
   - `load_data(path: str | Path) -> pd.DataFrame` — auto-detect format from file extension and dispatch to correct loader
   - Raise clear `ValueError` for missing columns or bad format

2. Create `src/backtest/data/provider.py`:
   - `DataProvider` class:
     - `__init__(self, df: pd.DataFrame, symbol: str)`
     - `filter_date_range(start: datetime | None, end: datetime | None) -> self`
     - `__iter__` yields `Candle` objects one bar at a time
     - `__len__` returns number of bars
     - `reset()` method to restart iteration
   - `MultiDataProvider` class (optional, for multi-symbol):
     - Takes dict of `{symbol: DataProvider}`
     - Yields candles aligned by timestamp

3. Create a sample CSV data file at `data/sample/btc_usdt_1h.csv`:
   - Generate ~500 rows of realistic-looking BTC/USDT 1-hour OHLCV data
   - Use a Python script to generate: start from price ~30000, random walk with realistic spreads between OHLC
   - Columns: `timestamp,open,high,low,close,volume`
   - Timestamps should be hourly from 2024-01-01 UTC

4. Verify:
   - Run: `uv run python -c "from backtest.data.loader import load_data; from backtest.data.provider import DataProvider; df = load_data('data/sample/btc_usdt_1h.csv'); dp = DataProvider(df, 'BTC/USDT'); candle = next(iter(dp)); print(f'First candle: {candle}'); print('Phase 2 OK')"`
