import logging
import argparse
from backtest.engine import BacktestEngine
from backtest.data import DuckDBDataHandler
from backtest.execution import SimulatedBroker
from strategies.rule_based import SmaCrossStrategy, RSIStrategy, BreakoutStrategy
from strategies.ml.ml_strategy import MLStrategy

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(description="Backtest Runner")
    parser.add_argument(
        "--db",
        type=str,
        default="../trading-data-pipeline/data/trading.db",
        help="Path to DuckDB",
    )
    parser.add_argument(
        "--symbol", type=str, default="BTC/USDT", help="Symbol to backtest"
    )
    parser.add_argument("--timeframe", type=str, default="1h", help="Timeframe")
    parser.add_argument(
        "--strategy",
        type=str,
        default="sma",
        choices=["sma", "rsi", "breakout", "ml"],
        help="Strategy to run",
    )

    args = parser.parse_args()

    # Setup
    engine = BacktestEngine(initial_capital=100000.0)

    engine.data_handler = DuckDBDataHandler(
        db_path=args.db,
        symbol=args.symbol,
        timeframe=args.timeframe,
        events_queue=engine.events,
    )

    engine.execution_handler = SimulatedBroker(
        events_queue=engine.events, commission=0.001
    )

    # Select Strategy
    if args.strategy == "sma":
        engine.strategy = SmaCrossStrategy(
            symbol=args.symbol, fast_period=20, slow_period=50
        )
    elif args.strategy == "rsi":
        engine.strategy = RSIStrategy(
            symbol=args.symbol, period=14, oversold=30, overbought=70
        )
    elif args.strategy == "breakout":
        engine.strategy = BreakoutStrategy(symbol=args.symbol, period=20)
    elif args.strategy == "ml":
        engine.strategy = MLStrategy(
            symbol=args.symbol, model_path="../trading-ml-lab/models/rf_latest.pkl"
        )

    # Run
    engine.run()


if __name__ == "__main__":
    main()
