from portfolio.portfolio import Portfolio
from ..interfaces.signal_generator import ISignalGenerator
from event.event import DataEvent
from dataclasses import dataclass, field
from queue import Queue
from data_provider.data_provider import DataProvider
from event.event import SignalEvent, SignalType, OrderType
import polars as pl


@dataclass
class SignalMACrossover(ISignalGenerator):
    event_queue: Queue
    data_provider: DataProvider
    portfolio: Portfolio
    timeframe: str
    fast_period: int
    slow_period: int

    def __pos_init__(self):
        # 1. Asignación y lógica de mínimos (reemplaza tu lógica del if inline)
        self.fast_period = self.fast_period if self.fast_period > 1 else 2
        self.slow_period = self.slow_period if self.slow_period > 2 else 3

        # 2. Validación
        if self.fast_period >= self.slow_period:
            raise ValueError(
                f"ERROR: el periodo rápido ({self.fast_period}) es mayor o igual "
                f"al periodo lento ({self.slow_period})"
            )

    def __post_init__(self):
        pass

    def _create_and_put_signal_event(
        self,
        symbol: str,
        signal: SignalType,
        target_order: OrderType,
        target_price: float,
        magic_numbre: int,
        stop_loss: float,
        take_profit: float,
    ):
        signal_event = SignalEvent(
            symbol=symbol,
            signal=signal,
            target_order=target_order,
            target_price=target_price,
            magic_numbre=magic_numbre,
            stop_loss=stop_loss,
            take_profit=take_profit,
        )
        self.event_queue.put(signal_event)

    def generate_signal(self, data_event: DataEvent) -> None:
        symbol = data_event.symbol

        timeframe = self.timeframe
        # Recuperamos los datos para calcular las medias móviles

        df_ar_data = self.data_provider.get_latest_close_bars(symbol, timeframe)
        open_positions = self.portfolio.get_number_of_strategy_opne_position_by_symbol(
            symbol
        )
        fasta_ma = df_ar_data.get_column("close").rolling_mean(self.fast_period).last()
        slowa_ma = df_ar_data.get_column("close").last()
        # Detectar cuando hay un cruese
        if isinstance(fasta_ma, float) and isinstance(slowa_ma, float):
            if open_positions["LONG"] == 0 and fasta_ma > slowa_ma:
                signal = SignalType.BUY

            elif open_positions["SHORT"] == 0 and slowa_ma > fasta_ma:
                signal = SignalType.SELL
            else:
                signal = None

            if signal is not None:
                self._create_and_put_signal_event(
                    symbol=symbol,
                    signal=signal,
                    target_order=OrderType.MARKET,
                    target_price=0.0,
                    magic_numbre=self.portfolio.magic_number,
                    stop_loss=0.0,
                    take_profit=0.0,
                )
