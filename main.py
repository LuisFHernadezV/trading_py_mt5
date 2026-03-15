from order_executor.order_executor import OrderExecutor
from platform_connector.platform_connector import PlatformConnector
from data_provider.data_provider import DataProvider
from queue import Queue
from signal_generator.properties.signal_generator_properties import MACrossoverProps
from trading_director.trading_director import TradingDirector
from signal_generator.signals.signal_ma_crossover import SignalMACrossover
from position_sizer.position_sizer import PositionSizer
from position_sizer.properties.position_sizer_properties import (
    MinSizingProps,
    FixedSizingProps,
)
from portfolio.portfolio import Portfolio
from risk_manager.risk_manager import RiskManager
from risk_manager.properties.risk_manager_properties import MaxLeverageRiskFactorProps
from notifications.notifications import (
    TelegramNotificationProperties,
    NotificationService,
)
from dotenv import load_dotenv, find_dotenv
import os
from signal_generator.signal_generator import SignalGenerator


def main():
    load_dotenv(find_dotenv())
    telegram_token = os.getenv("TELEGRAM_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    if telegram_token is None:
        raise Exception(f"Telegram token not found {telegram_token=}")
    if chat_id is None:
        raise Exception(f"Chat id not found {chat_id=}")

    symbols = ["EURUSD"]  # , "USDJPY", "SP500", "XAUUSD", "XTIUSD", "GBPUSD"]
    event_queue = Queue()
    timeframe = "1min"
    magic_number = 12345
    fast_period: int = 10
    slow_period: int = 5

    PlatformConnector(symbols)
    data_provider = DataProvider(
        event_queue=event_queue, symbols=symbols, timeframe=timeframe
    )
    portfolio = Portfolio(magic_number=magic_number)
    order_executor = OrderExecutor(event_queue=event_queue, portfolio=portfolio)
    signal_generator = SignalGenerator(
        event_queue=event_queue,
        data_provider=data_provider,
        portfolio=portfolio,
        order_executor=order_executor,
        signal_properties=MACrossoverProps(
            timeframe=timeframe, fast_period=fast_period, slow_period=slow_period
        ),
    )
    position_sizer = PositionSizer(
        event_queue=event_queue,
        data_provider=data_provider,
        sizing_properties=FixedSizingProps(volume=0.09),
    )
    risk_manager = RiskManager(
        event_queue=event_queue,
        data_provider=data_provider,
        portfolio=portfolio,
        risk_properties=MaxLeverageRiskFactorProps(max_leverage_factor=5.0),
    )
    notification_service = NotificationService(
        properties=TelegramNotificationProperties(
            token=telegram_token,
            chat_id=chat_id,
        )
    )

    # Create the trading director
    trading_director = TradingDirector(
        event_queue=event_queue,
        data_provider=data_provider,
        signal_generator=signal_generator,
        position_sizer=position_sizer,
        risk_manager=risk_manager,
        order_executor=order_executor,
        notification_service=notification_service,
    )
    trading_director.execute()


if __name__ == "__main__":
    main()
