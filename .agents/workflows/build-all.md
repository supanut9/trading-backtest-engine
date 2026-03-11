---
description: Build all phases of the backtest engine sequentially (Phase 1 through 7)
---

# Build All Phases

// turbo-all

Run all phases of the backtest engine in order. Each phase builds on the previous one.

## Steps

1. Execute `/build-phase1` — Project scaffold & core data models
2. Execute `/build-phase2` — Data ingestion layer
3. Execute `/build-phase3` — Backtest engine core
4. Execute `/build-phase4` — Strategy framework & built-in strategies
5. Execute `/build-phase5` — Performance analytics & reporting
6. Execute `/build-phase6` — CLI & configuration
7. Execute `/build-phase7` — Tests & verification

Execute each phase sequentially. After each phase, verify it works before moving to the next.
If a phase fails, fix the issues before proceeding.
