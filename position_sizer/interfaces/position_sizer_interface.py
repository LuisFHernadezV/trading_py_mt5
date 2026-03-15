from typing import Protocol
from event.event import SignalEvent
from data_provider.data_provider import DataProvider


class IPositionSizer(Protocol):
    def size_signal(
        self, signal_event: SignalEvent, data_provider: DataProvider
    ) -> float | None: ...
