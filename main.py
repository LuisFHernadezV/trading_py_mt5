from platform_connector.platform_connector import PlatformConnector
from data_provider.data_provider import DataProvider
from queue import Queue
from trading_director.trading_director import TradingDirector
from signal_generator.signals.signal_ma_crossover import SignalMACrossover


def main():
    symbols = ["EURUSD", "USDJPY"]  # , "SP500", "XAUUSD", "XTIUSD", "GBPUSD"]
    event_queue = Queue()
    timeframe = "1min"
    fast_period: int = 25
    slow_period: int = 50

    PlatformConnector(symbols)
    data_provider = DataProvider(
        event_queue=event_queue, symbols=symbols, timeframe=timeframe
    )
    signal_generator = SignalMACrossover(
        event_queue=event_queue,
        data_provider=data_provider,
        timeframe=timeframe,
        fast_period=fast_period,
        slow_period=slow_period,
    )
    # Create the trading director
    trading_director = TradingDirector(
        event_queue=event_queue,
        data_provider=data_provider,
        signal_generator=signal_generator,
    )
    trading_director.execute()


if __name__ == "__main__":
    main()
