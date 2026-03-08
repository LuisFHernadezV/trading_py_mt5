from dataclasses import dataclass
from signal_generator.interfaces.signal_generator import ISignalGenerator
from queue import Queue
import queue
from data_provider.data_provider import DataProvider
from typing import Callable
from event.event import DataEvent, SignalEvent
import time
from datetime import datetime


@dataclass
class TradingDirector:
    event_queue: Queue

    # Referencia de los diferentes módulos
    data_provider: DataProvider
    signal_generator: ISignalGenerator
    continue_trading: bool = True
    # Gestionamos los eventos de tipo DataEvent

    def __post_init__(self):
        self.event_handler: dict[str, Callable] = {
            "DATA": self._hanle_data_event,
            "SIGNAL": self._hanle_signal_event,
        }

    def _deteprint(self) -> str:
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def _hanle_signal_event(self, event: SignalEvent) -> None:
        print(
            f"{self._deteprint()} Received signal event: {event.symbol} - {
                event.signal
            }"
        )

    def _hanle_data_event(self, event: DataEvent) -> None:
        print(
            f"time consol: {self._deteprint()} time data event: {
                self._deteprint()
            } Received data event: {event.symbol} - Last close pricing: {
                event.data.get_column('close').last()
            }"
        )
        self.signal_generator.generate_signal(event)

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
