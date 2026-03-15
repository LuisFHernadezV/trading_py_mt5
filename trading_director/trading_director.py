from dataclasses import dataclass
from order_executor.order_executor import OrderExecutor
from position_sizer.position_sizer import PositionSizer
from risk_manager.risk_manager import RiskManager
from signal_generator.interfaces.signal_generator import ISignalGenerator
from queue import Queue
import queue
from data_provider.data_provider import DataProvider
from typing import Callable
from event.event import (
    DataEvent,
    ExecutionEvent,
    OrderEvent,
    PlacedPendingOrderEvent,
    SignalEvent,
    SizingEvent,
)
import time
from datetime import datetime
from utils.utils import Utils
from notifications.notifications import NotificationService


@dataclass
class TradingDirector:
    event_queue: Queue

    # Referencia de los diferentes módulos
    data_provider: DataProvider
    signal_generator: ISignalGenerator
    position_sizer: PositionSizer
    risk_manager: RiskManager
    order_executor: OrderExecutor
    notification_service: NotificationService
    continue_trading: bool = True
    # Gestionamos los eventos de tipo DataEvent

    def __post_init__(self):
        self.event_handler: dict[str, Callable] = {
            "DATA": self._handle_data_event,
            "SIGNAL": self._handle_signal_event,
            "SIZE": self._handle_sizing_event,
            "ORDER": self._handle_order_event,
            "EXECUTION": self._handle_execution_event,
            "PENDING": self._handle_pending_order_event,
        }

    def _handle_execution_event(self, event: ExecutionEvent) -> None:
        """
        Handle the execution event.

        Args:
            event (ExecutionEvent): The execution event object.

        Returns:
            None
        """
        print(
            f"{Utils.dateprint()} - Recibido EXECUTION EVENT {event.signal} en {
                event.symbol
            } con volumen {event.volume} al precio {event.fill_price}"
        )
        self._process_execution_or_pending_events(event)

    def _handle_order_event(self, event: OrderEvent) -> None:

        print(
            f"{self._deteprint()} Received order event with volume: {event.volume} for {
                event.signal
            } in {event.symbol}"
        )
        self.order_executor.execute_order(event)

    def _handle_pending_order_event(self, event: PlacedPendingOrderEvent):
        """
        Handle the pending order event.

        Args:
            event (PlacedPendingOrderEvent): The pending order event object.

        Returns:
            None
        """
        print(
            f"{Utils.dateprint()} - Recibido PLACED PENDING ORDER EVENT con volumen {
                event.volume
            } para {event.signal} {event.target_order} en {event.symbol} al precio {
                event.target_price
            }"
        )
        self._process_execution_or_pending_events(event)

    def _deteprint(self) -> str:
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def _handle_sizing_event(self, event: SizingEvent) -> None:
        print(
            f"{Utils.dateprint()} Received size event with volume: {event.volume} for {
                event.signal
            } in {event.symbol}"
        )
        self.risk_manager.assess_order(event)

    def _handle_signal_event(self, event: SignalEvent) -> None:
        print(
            f"{Utils.dateprint()} Received signal event: {event.symbol} - {
                event.signal
            }"
        )
        self.position_sizer.size_signal(event, self.data_provider)

    def _handle_data_event(self, event: DataEvent) -> None:
        print(
            f"{Utils.dateprint()} time data event: {
                Utils.dateprint()
            } Received data event: {event.symbol} - Last close pricing: {
                event.data.get_column('close').last()
            }"
        )
        self.signal_generator.generate_signal(event)

    def _hande_none_event(self, event):
        print(f"{Utils.dateprint()} Received None event: {event}")
        self.continue_trading = False

    def _handle_unknown_event(self, event):
        print(f"{Utils.dateprint()} Received unknown event: {event}")
        self.continue_trading = False

    def execute(self) -> None:
        while self.continue_trading:
            try:
                event = self.event_queue.get(block=False)

                if event is not None:
                    handler = self.event_handler.get(
                        event.event_type.name, self._handle_unknown_event
                    )
                    handler(event)
                else:
                    self._hande_none_event(event)
            except queue.Empty:
                self.data_provider.check_for_new_data()
            finally:
                time.sleep(0.01)

    # Utilizar el | es para python 3.10 o superior
    def _process_execution_or_pending_events(
        self, event: ExecutionEvent | PlacedPendingOrderEvent
    ):
        """
        Process the execution or pending events.

        Args:
            event (ExecutionEvent | PlacedPendingOrderEvent): The event to be processed.

        Returns:
            None
        """
        if isinstance(event, ExecutionEvent):
            self.notification_service.send_notification(
                title=f"{event.symbol} - MARKET ORDER",
                message=f"{Utils.dateprint()} - Ejecutada MARKET ORDER {
                    event.signal
                } en {event.symbol} con volumen {event.volume} al precio {
                    event.fill_price
                }",
            )
        elif isinstance(event, PlacedPendingOrderEvent):
            self.notification_service.send_notification(
                title=f"{event.symbol} - PENDING PLACED",
                message=f"{Utils.dateprint()} - Colocada PENDING ORDER con volumen {
                    event.volume
                } para {event.signal} {event.target_order} en {event.symbol} al precio {
                    event.target_price
                }",
            )
        else:
            pass
