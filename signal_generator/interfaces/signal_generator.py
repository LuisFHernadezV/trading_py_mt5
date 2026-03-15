from order_executor.order_executor import OrderExecutor
from portfolio.portfolio import Portfolio
from typing import Protocol
from data_provider.data_provider import DataProvider
from event.event import DataEvent, SignalEvent


class ISignalGenerator(Protocol):
    def generate_signal(
        self,
        data_event: DataEvent,
        data_provider: DataProvider | None = None,
        portfolio: Portfolio | None = None,
        order_executor: OrderExecutor | None = None,
    ) -> SignalEvent | None: ...
