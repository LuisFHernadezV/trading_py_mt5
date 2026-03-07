from platform_connector.platform_connector import PlatformConnector
from data_provider.data_provider import DataProvider
from queue import Queue
from trading_director.trading_director import TradingDirector


def main():
    symbols = ["EURUSD", "USDJPY", "SP500", "XAUUSD", "XTIUSD", "GBPUSD"]
    event_queue = Queue()
    timeframe = "1min"
    connect = PlatformConnector(symbols)
    data_provider = DataProvider(
        event_queue=event_queue, symbols=symbols, timeframe=timeframe
    )
    # Create the trading director
    trading_director = TradingDirector(
        event_queue=event_queue, data_provider=data_provider
    )
    trading_director.execute()


if __name__ == "__main__":
    main()
