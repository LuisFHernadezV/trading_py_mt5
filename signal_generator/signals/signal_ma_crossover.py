from order_executor.order_executor import OrderExecutor
from portfolio.portfolio import Portfolio
from signal_generator.properties.signal_generator_properties import MACrossoverProps
from ..interfaces.signal_generator import ISignalGenerator
from event.event import DataEvent
from dataclasses import dataclass
from data_provider.data_provider import DataProvider
from event.event import SignalEvent, SignalType, OrderType


@dataclass
class SignalMACrossover(ISignalGenerator):
    properties: MACrossoverProps

    def __pos_init__(self):

        # 1. Asignación y lógica de mínimos (reemplaza tu lógica del if inline)
        self.fast_period = (
            self.properties.fast_period if self.properties.fast_period > 1 else 2
        )
        self.slow_period = (
            self.properties.slow_period if self.properties.slow_period > 3 else 3
        )

        # 2. Validación
        if self.fast_period >= self.slow_period:
            raise ValueError(
                f"ERROR: el periodo rápido ({self.fast_period}) es mayor o igual "
                f"al periodo lento ({self.slow_period})"
            )

    def __post_init__(self):
        pass

    def generate_signal(
        self,
        data_event: DataEvent,
        data_provider: DataProvider | None = None,
        portfolio: Portfolio | None = None,
        order_executor: OrderExecutor | None = None,
    ):
        if data_provider is None:
            raise ValueError("data_provider is None")
        if portfolio is None:
            raise ValueError("portfolio is None")
        if order_executor is None:
            raise ValueError("order_executor is None")

        symbol = data_event.symbol

        timeframe = self.properties.timeframe
        # Recuperamos los datos para calcular las medias móviles

        df_ar_data = data_provider.get_latest_close_bars(symbol, timeframe)
        open_positions = portfolio.get_number_of_strategy_open_position_by_symbol(
            symbol
        )
        fast_ma = (
            df_ar_data.get_column("close")
            .rolling_mean(self.properties.fast_period)
            .last()
        )
        slow_ma = df_ar_data.get_column("close").last()
        # Detectar cuando hay un cruse
        if isinstance(fast_ma, float) and isinstance(slow_ma, float):
            if open_positions["LONG"] == 0 and fast_ma > slow_ma:
                if open_positions["SHORT"] > 0:
                    order_executor.close_strategy_short_positions_by_symbol(symbol)
                signal = SignalType.BUY

            elif open_positions["SHORT"] == 0 and slow_ma > fast_ma:
                if open_positions["LONG"] > 0:
                    order_executor.close_strategy_long_positions_by_symbol(symbol)
                signal = SignalType.SELL
            else:
                signal = None

            if signal is not None:
                signal_event = SignalEvent(
                    symbol=symbol,
                    signal=signal,
                    target_order=OrderType.MARKET,
                    target_price=0,
                    magic_number=portfolio.magic_number,
                    stop_loss=0,
                    take_profit=0,
                )
                return signal_event
