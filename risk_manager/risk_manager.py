from event.event import SizingEvent, OrderEvent
from portfolio.portfolio import Portfolio
from data_provider.data_provider import DataProvider
from risk_manager.interfaces.risk_manager_interface import IRiskManager
from queue import Queue
from .properties.risk_manager_properties import (
    BaseRiskProps,
    MaxLeverageRiskFactorProps,
)
from .risk_managers.max_leverage_factor_risk_manager import (
    MaxLeverageFactorRiskManager,
)
from utils.utils import Utils
import MetaTrader5 as mt5


class RiskManager(IRiskManager):
    def __init__(
        self,
        event_queue: Queue,
        data_provider: DataProvider,
        portfolio: Portfolio,
        risk_properties: BaseRiskProps,
    ):
        self.event_queue = event_queue
        self.data_provider = data_provider
        self.portfolio = portfolio
        self.risk_properties = risk_properties
        self.risk_management_method = self._get_risk_manager_method(risk_properties)

    def assess_order(
        self,
        sizing_event: SizingEvent,
        current_positions_value_acc_ccy: float | None = None,
        new_position_value_acc_ccy: float | None = None,
    ) -> None:
        """
        Assess the order based on the risk management method and create an order event if the new volume is greater than 0.

        Args:
            sizing_event (SizingEvent): The sizing event containing information about the order.

        Returns:
            None
        """

        # Obtenemos el valor de todas las posiciones abiertas por la estrategia en la divisa de la cuenta
        current_position_value = (
            self._compute_current_value_of_positions_in_account_currency()
        )

        # Obtenemos el valor que tendría la nueva posición, también en la divisa de la cuenta
        position_type = (
            mt5.ORDER_TYPE_BUY if sizing_event.signal == "BUY" else mt5.ORDER_TYPE_SELL
        )
        new_position_value = self._compute_value_of_position_in_account_currency(
            sizing_event.symbol, sizing_event.volume, position_type
        )

        # Obtenemos el nuevo volumen de la operación que queremos ejecutar después de pasar por el risk manager
        new_volume = self.risk_management_method.assess_order(
            sizing_event, current_position_value, new_position_value
        )
        if new_volume is None:
            return None

        # Evaluamos el nuevo volumen
        if new_volume > 0.0:
            # colocar el order event a la cola de eventos
            self._create_and_put_order_event(sizing_event, new_volume)

    def _compute_current_value_of_positions_in_account_currency(self) -> float:
        current_positions = self.portfolio.get_strategy_open_positions()
        total_value = 0.0
        # Calculamos el valor de las posiciones abiertas
        for position in current_positions:
            total_value += self._compute_value_of_position_in_account_currency(
                position.symbol, position.volume, position.type
            )
        return total_value

    def _compute_value_of_position_in_account_currency(
        self, symbol: str, volume: float, position_type: int
    ) -> float:
        """
        Computes the value of a position in the account currency.

        Args:
            symbol (str): The symbol of the position.
            volume (float): The volume of the position.
            position_type (int): The type of the position.

        Returns:
            float: The value of the position in the account currency.
        """
        symbol_info = mt5.symbol_info(symbol)

        # Unidades operadas en las unidades del symbol: (cantidad de moneda base, barriles de petroleo, onzas de oro)
        traded_units = volume * symbol_info.trade_contract_size

        # Valor de las unidades operadas en la divisa cotizada del símbolo (USD para el oro, USD para el petróleo, CHF para el GBPCHF, EUR para el DAX)
        value_traded_in_profit_ccy = (
            traded_units * self.data_provider.get_latest_tick(symbol)["bid"]
        )

        # Valor de las unidades operadas en la divisa de nuestra cuenta de trading (la cuenta en el broker, la cuenta MT5)
        value_traded_in_account_ccy = Utils.convert_currency_amount_to_another_currency(
            value_traded_in_profit_ccy,
            symbol_info.currency_profit,
            mt5.account_info().currency,
        )

        if position_type == mt5.ORDER_TYPE_SELL:
            return -value_traded_in_account_ccy
        else:
            return value_traded_in_account_ccy

    def _create_and_put_order_event(
        self, sizing_event: SizingEvent, volume: float
    ) -> None:
        """
        Creates an OrderEvent based on the given SizingEvent and volume, and puts it into the events queue.

        Args:
            sizing_event (SizingEvent): The sizing event to create the order event from.
            volume (float): The volume for the order event.

        Returns:
            None
        """
        # Creamos el Order event a partir del sizing event y el volume
        order_event = OrderEvent(
            symbol=sizing_event.symbol,
            signal=sizing_event.signal,
            target_order=sizing_event.target_order,
            target_price=sizing_event.target_price,
            magic_number=sizing_event.magic_number,
            stop_loss=sizing_event.stop_loss,
            take_profit=sizing_event.take_profit,
            volume=volume,
        )

        # Colocamos el order event a la cola de eventos
        self.event_queue.put(order_event)

    def _get_risk_manager_method(self, risk_props: BaseRiskProps) -> IRiskManager:
        """
        Returns the appropriate risk management method based on the given risk properties.

        Args:
            risk_props (BaseRiskProps): The risk properties object.

        Returns:
            IRiskManager: An instance of the appropriate risk manager.

        Raises:
            Exception: If the risk management method is unknown.
        """
        if isinstance(risk_props, MaxLeverageRiskFactorProps):
            return MaxLeverageFactorRiskManager(risk_props)
        raise Exception(f"ERROR: Método de Risk Mgmt desconocido: {risk_props}")
