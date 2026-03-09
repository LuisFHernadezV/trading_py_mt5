from position_sizer.position_sizers.risk_pct_position_sizer import RiskPctPositionSizer
from position_sizer.position_sizers.fixed_size_position_sizer import (
    FixedSizePositionSizer,
)
from position_sizer.position_sizers.min_size_position_sizer import MinSizePositionSizer
from position_sizer.interfaces.position_sizer_interface import IPositionSizer
from event.event import SignalEvent, SizingEvent, SizingEvent
from data_provider.data_provider import DataProvider
from queue import Queue
import MetaTrader5 as mt5

from position_sizer.properties.position_sizer_properties import (
    BaseSizerProps,
    FixedSizingProps,
    MinSizingProps,
    RiskPctSizingProps,
)


class PositionSizer(IPositionSizer):
    def __init__(
        self,
        event_queue: Queue,
        data_provider: DataProvider,
        sizing_properties: BaseSizerProps,
    ):
        self.event_queue = event_queue
        self.position_size_method = self._get_position_sizing_method(sizing_properties)
        self.data_provider = data_provider

    def _get_position_sizing_method(
        self, sizing_props: BaseSizerProps
    ) -> IPositionSizer:
        """
        Devuelve una instancia del position sizer apropiado en funcion del objeto de propiedades recibido
        """
        if isinstance(sizing_props, MinSizingProps):
            return MinSizePositionSizer()
        elif isinstance(sizing_props, FixedSizingProps):
            return FixedSizePositionSizer(properties=sizing_props)
        elif isinstance(sizing_props, RiskPctSizingProps):
            return RiskPctPositionSizer(properties=sizing_props)

        raise Exception("Invalid sizing properties")

    def _create_and_put_sizing_event(
        self, signal_event: SignalEvent, volume: float
    ) -> None:

        self.event_queue.put(
            SizingEvent(
                symbol=signal_event.symbol,
                signal=signal_event.signal,
                target_order=signal_event.target_order,
                target_price=signal_event.target_price,
                magic_numbre=signal_event.magic_numbre,
                stop_loss=signal_event.stop_loss,
                take_profit=signal_event.take_profit,
                volume=volume,
            )
        )

    def size_signal(
        self, signal_event: SignalEvent, data_provider: DataProvider
    ) -> float:
        volume = self.position_size_method.size_signal(signal_event, self.data_provider)

        if volume < mt5.symbol_info(signal_event.symbol).volume_min:
            print(
                f"Error: Volume {volume} is less than min volume {signal_event.symbol}"
            )

        return 0
