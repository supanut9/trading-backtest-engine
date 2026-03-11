---
description: Phase 6 - Build CLI interface and YAML configuration system
---

# Phase 6: CLI & Configuration

// turbo-all

## Prerequisites
- Phase 1-5 must be completed

## Steps

1. Create `config/default.yaml`:
   ```yaml
   backtest:
     initial_capital: 10000.0
     commission_rate: 0.001
     slippage_rate: 0.0005
     start_date: null  # null = use all data
     end_date: null

   strategy:
     name: sma_cross
     params:
       symbol: BTC/USDT
       fast_period: 10
       slow_period: 30
       position_size: 1.0

   data:
     path: data/sample/btc_usdt_1h.csv
     format: auto  # auto, csv, parquet

   report:
     terminal: true
     html: true
     output_dir: reports/
   ```

2. Create `src/backtest/config.py`:
   - `BacktestConfig` dataclass that maps from YAML
   - `load_config(path: str) -> BacktestConfig`
   - Support merging: default.yaml + user override file + CLI args

3. Create/update `src/backtest/cli.py`:
   - Use `click` library
   - Commands:
     - `backtest run` — run backtest with options:
       - `--config PATH` (default: config/default.yaml)
       - `--strategy NAME` (override strategy from config)
       - `--data PATH` (override data path)
       - `--capital FLOAT` (override initial capital)
       - `--output-dir PATH` (where to save reports)
     - `backtest list-strategies` — list all registered strategies with descriptions
   - Strategy registry: dict mapping name → class (sma_cross, rsi_mean_revert)
   - Wire everything together: load config → load data → create provider → create strategy → create broker → create portfolio → create engine → run → compute metrics → generate reports

4. Update `pyproject.toml` entry point:
   - `[project.scripts]` → `backtest = "backtest.cli:main"`

5. Verify:
   - Run: `uv run backtest run` (uses default config)
   - Run: `uv run backtest run --strategy rsi_mean_revert --capital 50000`
   - Run: `uv run backtest list-strategies`
   - Confirm output shows metrics and HTML report is generated
