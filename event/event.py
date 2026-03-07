import polars as pl
from dataclasses import dataclass
from enum import StrEnum, auto
from pydantic import BaseModel


class EventType(StrEnum):
    DATA = auto()
    SIGNAL = auto()


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
    magic_numbre: int
    stop_loss: float
    take_profit: float
