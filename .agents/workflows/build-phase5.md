---
description: Phase 5 - Build performance analytics and reporting (metrics + HTML report)
---

# Phase 5: Performance Analytics & Reporting

// turbo-all

## Prerequisites
- Phase 1-4 must be completed

## Steps

1. Create `src/backtest/analytics/metrics.py`:
   - `calculate_metrics(result: BacktestResult, risk_free_rate: float = 0.0) -> dict`:
     - **Total Return** (%) = (final_equity - initial_capital) / initial_capital * 100
     - **Annualized Return** — based on actual trading period
     - **Sharpe Ratio** — annualized, from daily/bar returns
     - **Sortino Ratio** — using downside deviation only
     - **Max Drawdown** (%) — peak-to-trough from equity curve
     - **Max Drawdown Duration** — longest time in drawdown
     - **Win Rate** (%) — winning trades / total trades
     - **Profit Factor** — gross profit / gross loss
     - **Average Win / Average Loss**
     - **Total Trades**
     - **Expectancy** — average PnL per trade
   - Each metric should be a standalone function too (e.g. `sharpe_ratio(returns)`)
   - Handle edge cases: 0 trades, no losing trades, etc.

2. Create `src/backtest/analytics/report.py`:
   - `TerminalReport` class:
     - Uses `rich` library to print a formatted table of all metrics
     - Shows trade summary table (entry/exit time, side, PnL)
     - Color-codes positive (green) and negative (red) PnL
   - `HtmlReport` class:
     - Uses `jinja2` template to generate a self-contained HTML file
     - Includes equity curve chart using inline Chart.js (CDN link)
     - Includes drawdown chart
     - Metrics summary table
     - Individual trade table
     - Save to `reports/` directory
   - Create Jinja2 template at `src/backtest/analytics/templates/report.html`

3. Verify:
   - Run a full backtest with SMA cross → compute metrics → print terminal report
   - Generate HTML report and confirm the file is valid HTML
   - Check metric values are reasonable (Sharpe, drawdown, etc.)
