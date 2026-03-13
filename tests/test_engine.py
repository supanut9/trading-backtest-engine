import pytest
from datetime import datetime, timedelta
from backtest.engine import BacktestEngine
from backtest.events import Candle, DataEvent
from strategies.rule_based.sma_cross import SmaCrossStrategy
from backtest.execution import SimulatedBroker
class MockDataHandler:
    def __init__(self, events_queue, symbol="BTC/USDT"):
        self.events_queue = events_queue
        self.continue_backtest = True
        self.symbol = symbol
        self.timeframe = "1h"
        self.candles = [
            Candle(symbol, datetime.now() + timedelta(hours=i), 100 + i, 110 + i, 90 + i, 105 + i, 1.0)
            for i in range(10)
        ]
        self.idx = 0

    def stream_next_candle(self):
        if self.idx < len(self.candles):
            candle = self.candles[self.idx]
            self.events_queue.put(DataEvent(candle=candle))
            self.idx += 1
        else:
            self.continue_backtest = False

def test_engine_run():
    engine = BacktestEngine(initial_capital=10000.0)
    engine.data_handler = MockDataHandler(engine.events)
    engine.execution_handler = SimulatedBroker(engine.events)
    engine.strategy = SmaCrossStrategy(symbol="BTC/USDT", fast_period=2, slow_period=5)
    
    metrics = engine.run()
    
    assert "total_return" in metrics
    assert "final_equity" in metrics
    assert "trades" in metrics
    assert metrics["final_equity"] > 0
