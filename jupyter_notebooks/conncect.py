import MetaTrader5 as mt5
import os
from dotenv import load_dotenv, find_dotenv
import polars as pl

load_dotenv(find_dotenv())

mt5.initialize(
    path=os.getenv("MT5_PATH"),
    login=int(os.getenv("MT5_LOGIN")),
    password=os.getenv("MT5_PASSWORD"),
    server=os.getenv("MT5_SERVER"),
    timeout=int(os.getenv("MT5_TIMEOUT")),
    portable=eval(os.getenv("MT5_PORTABLE")),
)

symbol = "EURUSD"
timeframe = mt5.TIMEFRAME_H1
from_position = 1
num_bars = 1

df_bars = pl.DataFrame(
    mt5.copy_rates_from_pos(symbol, timeframe, from_position, num_bars)
)
df_bars = df_bars.with_columns(pl.from_epoch("time", time_unit="s").alias("time"))
df_bars = df_bars.rename({"tick_volume": "tickvol", "real_volume": "vol"})
df_bars = df_bars.select(
    ["time", "open", "high", "low", "close", "tickvol", "vol", "spread"]
)


mt5.symbol_info_tick("EURUSD")._asdict()
