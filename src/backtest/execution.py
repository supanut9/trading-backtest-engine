import logging
from typing import Optional
from .events import FillEvent
from strategies import Candle, Order

logger = logging.getLogger(__name__)


class SimulatedBroker:
    def __init__(self, events_queue, commission: float = 0.001):
        self.events_queue = events_queue
        self.commission_rate = commission
        self.current_candle: Optional[Candle] = None

    def on_data(self, candle: Candle):
        self.current_candle = candle

    def execute_order(self, order: Order):
        """Simulate execution. For now, we fill at the close price of the current candle."""
        if not self.current_candle:
            logger.warning(f"No price data yet. Cannot fill order {order.symbol}")
            return

        # Simple simulation: use current candle's close price
        fill_price = self.current_candle.close
        commission = fill_price * order.size * self.commission_rate

        fill = FillEvent(order=order, fill_price=fill_price, commission=commission)
        self.events_queue.put(fill)
