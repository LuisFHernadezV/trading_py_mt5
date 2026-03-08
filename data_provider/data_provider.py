from dataclasses import dataclass, field
from event.event import DataEvent
import MetaTrader5 as mt5
import polars as pl
import datetime as dt
from queue import Queue


@dataclass
class DataProvider:
    event_queue: Queue
    symbols: list[str]
    timeframe: str
    last_bar_datatime: dict[str, dt.datetime] = field(init=False)

    def __post_init__(self):
        self.last_bar_datatime = {symbol: dt.datetime.min for symbol in self.symbols}

    def _map_timeframes(self, timeframe: str) -> int:
        timeframe_mapping = {
            "1min": mt5.TIMEFRAME_M1,
            "2min": mt5.TIMEFRAME_M2,
            "3min": mt5.TIMEFRAME_M3,
            "4min": mt5.TIMEFRAME_M4,
            "5min": mt5.TIMEFRAME_M5,
            "6min": mt5.TIMEFRAME_M6,
            "10min": mt5.TIMEFRAME_M10,
            "12min": mt5.TIMEFRAME_M12,
            "15min": mt5.TIMEFRAME_M15,
            "20min": mt5.TIMEFRAME_M20,
            "30min": mt5.TIMEFRAME_M30,
            "1h": mt5.TIMEFRAME_H1,
            "2h": mt5.TIMEFRAME_H2,
            "3h": mt5.TIMEFRAME_H3,
            "4h": mt5.TIMEFRAME_H4,
            "6h": mt5.TIMEFRAME_H6,
            "8h": mt5.TIMEFRAME_H8,
            "12h": mt5.TIMEFRAME_H12,
            "1d": mt5.TIMEFRAME_D1,
            "1w": mt5.TIMEFRAME_W1,
            "1M": mt5.TIMEFRAME_MN1,
        }
        if timeframe in timeframe_mapping.keys():
            return timeframe_mapping[timeframe]
        else:
            raise ValueError(f"Timeframe {timeframe} not supported")

    def get_latest_close_bars(
        self, symbol: str, timeframe: str, num_bars: int = 1
    ) -> pl.DataFrame:
        # Recuperamos los datos de la ultima vela
        try:
            timeframe_int = self._map_timeframes(timeframe)
            from_position = 1
            num_bars = num_bars if num_bars > 0 else 1
            bars_numpy_array = mt5.copy_rates_from_pos(
                symbol, timeframe_int, from_position, num_bars
            )
            if not bars_numpy_array:
                return pl.DataFrame()
            else:
                df_bars = pl.DataFrame(bars_numpy_array)
                if df_bars.is_empty():
                    return pl.DataFrame()
                # Cambiamos el formato de la fecha a datetime
                df_bars = df_bars.with_columns(
                    pl.from_epoch("time", time_unit="s").alias("time")
                )
                df_bars = df_bars.rename(
                    {"tick_volume": "tickvol", "real_volume": "vol"}
                )
                df_bars = df_bars.select(
                    ["time", "open", "high", "low", "close", "tickvol", "vol", "spread"]
                )
                return df_bars.sort("time")
        except Exception as e:
            print(f"Can't get latest close bar {symbol:} {timeframe:}")
            print(e)
            print(f"Mt5 error: {mt5.last_error()}")
            return pl.DataFrame()

    def get_latest_tick(self, symbol: str) -> dict[str, str]:
        try:
            tick = mt5.symbol_info_tick(symbol)
            if not tick:
                print(f"Can't get latest tick {symbol:}")
                print(f"Mt5 error: {mt5.last_error()}")
                return {}
            return tick._asdict()
        except Exception as e:
            print(f"Error: {e}")
            print(f"Mt5 error: {mt5.last_error()}")
            return {}

    def check_for_new_data(self) -> None:
        for symbol in self.symbols:
            df_latest_bar = self.get_latest_close_bars(symbol, self.timeframe)
            if df_latest_bar.is_empty():
                continue
            latest_bar = df_latest_bar.get_column("time").last()
            if isinstance(latest_bar, dt.datetime):
                if latest_bar > self.last_bar_datatime[symbol]:
                    self.last_bar_datatime[symbol] = latest_bar
                else:
                    continue
            else:
                continue

            data_event: DataEvent = DataEvent(symbol=symbol, data=df_latest_bar)

            self.event_queue.put(data_event)
