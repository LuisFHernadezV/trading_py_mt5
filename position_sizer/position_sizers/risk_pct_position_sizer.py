from data_provider.data_provider import DataProvider
from ..interfaces.position_sizer_interface import IPositionSizer
from event.event import SignalEvent
from ..properties.position_sizer_properties import RiskPctSizingProps
import MetaTrader5 as mt5


class RiskPctPositionSizer(IPositionSizer):
    def __init__(self, properties: RiskPctSizingProps):
        self.risk_pct = properties.risk_pct

    def size_signal(
        self, signal_event: SignalEvent, data_provider: DataProvider
    ) -> float:
        if self.risk_pct <= 0:
            print(f"Risk pct must be greater than 0 {self.risk_pct}")
            return 0.0

        if signal_event.stop_loss <= 0:
            print(f"Stop loss must be greater than 0 {signal_event.stop_loss}")
            return 0.0

        account_info = mt5.account_info()
        symbol_info = mt5.symbol_info(signal_event.symbol)

        # Recuperamos el precio de entrada estimado
        if signal_event.target_order == "MARKET":
            last_tick = data_provider.get_latest_tick(signal_event.symbol)
            entry_price = (
                last_tick["ask"] if signal_event.signal == "BUY" else last_tick["bid"]
            )
        else:
            entry_price = signal_event.target_price

        equity = account_info["equity"]
        volume_step = symbol_info["volume_step"]
        tick_size = symbol_info["trade_tick_size"]
        # account_currency = account_info["currency"]
        # symbol_profit_currency = symbol_info["currency_profit"]
        # contract_size = symbol_info["trade_contract_size"]
        # Cálculos auxiliares
        # tick_value_profit_currency = tick_size * contract_size

        # Convertir el tick value en profit ccy del symbol a la divisa de nuestra cuenta
        tick_value_account_currency = 5

        # Calculo del tamaño de la posición
        try:
            price_distance_in_integer_ticksize = int(
                abs(float(entry_price) - signal_event.stop_loss) / tick_size
            )
            monetary_risk = equity * self.risk_pct
            volume = monetary_risk / (
                price_distance_in_integer_ticksize * tick_value_account_currency
            )
            volume = round(volume / volume_step) * volume_step
            return volume
        except Exception as e:
            print(f"ERROR: No se pudo calcular el tamaño de la posición. Error: {e}")
            return 0.0
