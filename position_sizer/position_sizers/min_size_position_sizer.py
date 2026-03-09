from data_provider.data_provider import DataProvider
from ..interfaces.position_sizer_interface import IPositionSizer
from event.event import SignalEvent
from data_provider.data_provider import DataProvider


class MinSizePositionSizer(IPositionSizer):
    def size_signal(
        self, signal_event: SignalEvent, data_provider: DataProvider
    ) -> float:
        volume = mt5.symbol_info(signal_event.symbol).volume_min
        if volume is not None:
            return volume
        else:
            print(
                f"Error (MinSizePositionSizer): No se ha podido determinar el volumen mínimo para {
                    signal_event.symbol
                }"
            )
            return 0.0
