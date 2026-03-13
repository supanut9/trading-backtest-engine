import queue
import logging
from typing import Optional, List, Dict
from rich.table import Table
from rich.console import Console
from .events import Event, EventType, DataEvent, SignalEvent, OrderEvent, FillEvent
from .data import DuckDBDataHandler
from .execution import SimulatedBroker
from .analytics import PerformanceAnalytics
from .reports import ReportGenerator
from strategies import Portfolio, AbstractStrategy

logger = logging.getLogger(__name__)


class BacktestEngine:
    def __init__(self, initial_capital: float = 10000.0):
        self.events: queue.Queue[Event] = queue.Queue()
        self.portfolio = Portfolio(
            initial_capital=initial_capital, cash=initial_capital
        )
        self.strategy: Optional[AbstractStrategy] = None
        self.data_handler: Optional[DuckDBDataHandler] = None
        self.execution_handler: Optional[SimulatedBroker] = None
        self.is_running = False
        self.trades: List[Dict] = []

    def run(self):
        """Main event loop."""
        logger.info("Starting Backtest...")
        self.is_running = True

        if self.strategy:
            self.strategy.on_init()

        while self.is_running:
            # 1. Pull data if queue is empty
            if self.events.empty():
                assert self.data_handler is not None, "Data handler not initialized"
                if not self.data_handler.continue_backtest:
                    break
                self.data_handler.stream_next_candle()

            # 2. Process events
            try:
                event = self.events.get(block=False)
            except queue.Empty:
                continue

            if event.type == EventType.DATA:
                self._handle_data(event)
            elif event.type == EventType.SIGNAL:
                self._handle_signal(event)
            elif event.type == EventType.ORDER:
                self._handle_order(event)
            elif event.type == EventType.FILL:
                self._handle_fill(event)

        return self._summary()

    def _handle_data(self, event: DataEvent):
        """Forward data to strategy and execution."""
        # 1. Update position mark-to-market and take snapshot
        for position in self.portfolio.positions.values():
            position.mark_to_market(event.candle.close)

        self.portfolio.snapshot(event.candle.timestamp)

        # 2. Update broker price
        assert self.execution_handler is not None, "Execution handler not initialized"
        self.execution_handler.on_data(event.candle)

        # 3. Strategy generates new orders
        if self.strategy:
            new_orders = self.strategy.on_candle(event.candle, self.portfolio)
            for order in new_orders:
                self.events.put(OrderEvent(order=order))

    def _handle_signal(self, event: SignalEvent):
        """Handle raw signals (if strategy isn't automatic)."""
        pass

    def _handle_order(self, event: OrderEvent):
        """Process local orders through the broker."""
        assert self.execution_handler is not None, "Execution handler not initialized"
        self.execution_handler.execute_order(event.order)

    def _handle_fill(self, event: FillEvent):
        """Update portfolio after order is filled."""
        self.portfolio.update_position(event.order, event.fill_price, event.commission)
        
        # Track trade
        self.trades.append({
            "timestamp": event.order.timestamp.isoformat() if event.order.timestamp else None,
            "symbol": event.order.symbol,
            "side": event.order.side.value,
            "price": event.fill_price,
            "size": event.order.size,
            "commission": event.commission,
            "value": event.order.size * event.fill_price
        })
        
        logger.info(
            f"FILL: {event.order.side} {event.order.symbol} @ {event.fill_price}"
        )

    def _summary(self):
        logger.info("Backtest Complete.")

        metrics = PerformanceAnalytics.calculate_metrics(
            self.portfolio.history, self.portfolio.initial_capital
        )

        if not metrics:
            print("No history recorded.")
            return {}

        # Add trades to metrics
        metrics["trades"] = self.trades

        # CLI Table Summary
        console = Console()
        table = Table(title="Backtest Results Summary")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="magenta")

        table.add_row("Total Return", f"{metrics['total_return'] * 100:.2f}%")
        table.add_row("Max Drawdown", f"{metrics['max_drawdown'] * 100:.2f}%")
        table.add_row("Sharpe Ratio", f"{metrics['sharpe_ratio']:.2f}")
        table.add_row("Final Equity", f"{metrics['final_equity']:.2f}")
        table.add_row("Peak Equity", f"{metrics['peak_equity']:.2f}")
        table.add_row("Total Trades", f"{len(self.trades)}")

        console.print(table)

        # Generate HTML Report
        if self.data_handler:
            report_path = ReportGenerator.generate(
                metrics=metrics,
                strategy_name=self.strategy.name if self.strategy else "Unknown",
                symbol=self.data_handler.symbol,
                timeframe=self.data_handler.timeframe,
                initial_capital=self.portfolio.initial_capital,
                output_path="backtest_report.html",
            )
            logger.info(f"HTML Report generated at: {report_path}")

        return metrics
