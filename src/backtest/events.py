from dataclasses import dataclass
from enum import Enum
from strategies import Candle, Order, OrderSide, OrderType


class EventType(Enum):
    DATA = "DATA"
    SIGNAL = "SIGNAL"
    ORDER = "ORDER"
    FILL = "FILL"


@dataclass(kw_only=True)
class Event:
    type: EventType


@dataclass(kw_only=True)
class DataEvent(Event):
    candle: Candle
    type: EventType = EventType.DATA


@dataclass(kw_only=True)
class SignalEvent(Event):
    symbol: str
    side: OrderSide
    reason: str
    type: EventType = EventType.SIGNAL


@dataclass(kw_only=True)
class OrderEvent(Event):
    order: Order
    type: EventType = EventType.ORDER


@dataclass(kw_only=True)
class FillEvent(Event):
    order: Order
    fill_price: float
    commission: float
    type: EventType = EventType.FILL
