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


mt5.positions_get()
