from dataclasses import dataclass
from queue import Queue
from data_provider.data_provider import DataProvider
from event.event import DataEvent
from order_executor.order_executor import OrderExecutor
from portfolio.portfolio import Portfolio
from signal_generator.interfaces.signal_generator import ISignalGenerator
from signal_generator.properties.signal_generator_properties import (
    BaseSignalProps,
    MACrossoverProps,
)
from signal_generator.signals.signal_ma_crossover import SignalMACrossover


@dataclass()
class SignalGenerator(ISignalGenerator):
    event_queue: Queue
    data_provider: DataProvider
    portfolio: Portfolio
    order_executor: OrderExecutor
    signal_properties: BaseSignalProps

    def __post_init__(self):
        self.signal_generator_method = self._get_signal_generator_method(
            self.signal_properties
        )

    def _get_signal_generator_method(
        self, signal_properties: BaseSignalProps
    ) -> ISignalGenerator:

        if isinstance(signal_properties, MACrossoverProps):
            return SignalMACrossover(properties=signal_properties)
        else:
            raise Exception(f"Method not found for signal {signal_properties}")

    def generate_signal(
        self,
        data_event: DataEvent,
        data_provider: DataProvider | None = None,
        portfolio: Portfolio | None = None,
        order_executor: OrderExecutor | None = None,
    ) -> None:
        signal_event = self.signal_generator_method.generate_signal(
            data_event, self.data_provider, self.portfolio, self.order_executor
        )
        if signal_event is not None:
            self.event_queue.put(signal_event)
