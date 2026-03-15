import polars as pl
from enum import StrEnum, auto
from pydantic import BaseModel
from datetime import datetime


class EventType(StrEnum):
    DATA = auto()
    SIGNAL = auto()
    SIZING = auto()
    ORDER = auto()
    EXECUTION = auto()
    PENDING = auto()


class SignalType(StrEnum):
    BUY = auto()
    SELL = auto()


class OrderType(StrEnum):
    MARKET = auto()
    LIMIT = auto()
    STOP = auto()


class BaseEvent(BaseModel):
    event_type: EventType

    class Config:
        arbitrary_types_allowed = True


class DataEvent(BaseEvent):
    event_type: EventType = EventType.DATA
    symbol: str
    data: pl.DataFrame


class SignalEvent(BaseEvent):
    event_type: EventType = EventType.SIGNAL
    symbol: str
    signal: SignalType
    target_order: OrderType
    target_price: float
    magic_number: int
    stop_loss: float
    take_profit: float


class SizingEvent(BaseEvent):
    event_type: EventType = EventType.SIZING
    symbol: str
    signal: SignalType
    target_order: OrderType
    target_price: float
    magic_number: int
    stop_loss: float
    take_profit: float
    volume: float


class OrderEvent(BaseEvent):
    event_type: EventType = EventType.ORDER
    symbol: str
    signal: SignalType
    target_order: OrderType
    target_price: float
    magic_number: int
    stop_loss: float
    take_profit: float
    volume: float


class ExecutionEvent(BaseEvent):
    event_type: EventType = EventType.EXECUTION
    symbol: str
    signal: SignalType
    fill_price: float
    fill_time: datetime
    volume: float


class PlacedPendingOrderEvent(BaseEvent):
    """
    Represents an event for a placed pending order.

    Attributes:
        event_type (EventType): The type of the event (EventType.PENDING).
        symbol (str): The symbol of the order.
        signal (SignalType): The type of signal for the order.
        target_order (OrderType): The type of order to be placed.
        target_price (float): The target price for the order.
        magic_number (int): The magic number associated with the order.
        sl (float): The stop loss level for the order.
        tp (float): The take profit level for the order.
        volume (float): The volume of the order.
    """

    event_type: EventType = EventType.PENDING
    symbol: str
    signal: SignalType
    target_order: OrderType
    target_price: float
    magic_number: int
    stop_loss: float
    take_profit: float
    volume: float
