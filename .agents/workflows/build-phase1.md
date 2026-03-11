---
description: Phase 1 - Scaffold project and create core data models
---

# Phase 1: Project Scaffold & Core Data Models

// turbo-all

## Steps

1. Create `pyproject.toml` with the following config:
   - Project name: `trading-backtest-engine`
   - Python >= 3.12
   - Dependencies: `pandas`, `numpy`, `pyyaml`, `click`, `rich`, `jinja2`
   - Dev dependencies: `pytest`, `pytest-cov`
   - Entry point: `backtest = backtest.cli:main`
   - Source layout: `src/`

2. Create `README.md` with project title, description, and basic usage instructions.

3. Create directory structure:
   ```
   src/backtest/__init__.py
   src/backtest/data/__init__.py
   src/backtest/engine/__init__.py
   src/backtest/strategy/__init__.py
   src/backtest/analytics/__init__.py
   config/
   data/sample/
   tests/
   ```

4. Create `src/backtest/models.py` with these dataclasses and enums:
   - `Candle` dataclass: timestamp (datetime), open (float), high (float), low (float), close (float), volume (float)
   - `OrderSide` enum: BUY, SELL
   - `OrderType` enum: MARKET, LIMIT
   - `Order` dataclass: symbol (str), side (OrderSide), order_type (OrderType), size (float), price (float | None), timestamp (datetime)
   - `Fill` dataclass: order (Order), fill_price (float), commission (float), timestamp (datetime)
   - `Position` dataclass: symbol (str), side (OrderSide), entry_price (float), size (float), unrealized_pnl (float = 0.0) with method `mark_to_market(current_price)`
   - `Trade` dataclass: symbol (str), side (OrderSide), entry_price (float), exit_price (float), size (float), pnl (float), commission (float), entry_time (datetime), exit_time (datetime)
   - `PortfolioSnapshot` dataclass: timestamp (datetime), equity (float), cash (float), positions_value (float)

5. Run `uv init` if pyproject.toml needs it, then `uv sync` to install dependencies.

6. Verify by running: `uv run python -c "from backtest.models import Candle, Order, Position, Trade; print('Phase 1 OK')"`
