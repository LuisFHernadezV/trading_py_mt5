from dataclasses import dataclass
from queue import Queue
import queue
from data_provider.data_provider import DataProvider
from typing import Callable
from event.event import DataEvent
import time


@dataclass
class TradingDirector:
    event_queue: Queue

    # Referencia de los diferentes módulos
    data_provider: DataProvider
    continue_trading: bool = True
    # Gestionamos los eventos de tipo DataEvent

    def __post_init__(self):
        self.event_handler: dict[str, Callable] = {"DATA": self._hanle_data_event}

    def _hanle_data_event(self, event: DataEvent) -> None:
        print(
            f"{event.data.get_column('time').last()} New data event: {
                event.symbol
            } - Last close pricing: {event.data.get_column('close').last()}"
        )

    def execute(self) -> None:
        while self.continue_trading:
            try:
                event = self.event_queue.get(block=False)

                if event is not None:
                    handler = self.event_handler.get(event.event_type.name)
                    if handler:
                        handler(event)
            except queue.Empty:
                self.data_provider.check_for_new_data()
            finally:
                time.sleep(0.01)
