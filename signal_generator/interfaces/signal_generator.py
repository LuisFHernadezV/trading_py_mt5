from typing import Protocol
from event.event import DataEvent


class ISignalGenerator(Protocol):
    def generate_signal(self, data_event: DataEvent) -> None: ...
