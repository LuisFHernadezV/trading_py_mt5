from event.event import SizingEvent
from risk_manager.interfaces.risk_manager_interface import IRiskManager
from risk_manager.properties.risk_manager_properties import MaxLeverageRiskFactorProps
import MetaTrader5 as mt5
import sys
from utils.utils import Utils
from event.event import SizingEvent


class MaxLeverageFactorRiskManager(IRiskManager):
    def __init__(self, properties: MaxLeverageRiskFactorProps):
        self.properties = properties
        self.max_leverage_factor = properties.max_leverage_factor

    def _compute_leverege_factor(self, account_value_acc_ccy: float) -> float:
        account_equity = mt5.account_info().equity
        if account_equity <= 0:
            return sys.float_info.max
        return account_value_acc_ccy / account_equity

    def _check_expected_new_position_is_compliant_with_max_leverage_factor(
        self,
        sizing_event: SizingEvent,
        current_postion_value_acc_ccy: float,
        new_position_value_acc_ccy: float,
    ) -> bool:
        new_accout_value = current_postion_value_acc_ccy + new_position_value_acc_ccy
        new_leverage_factor = self._compute_leverege_factor(new_accout_value)

        if abs(new_leverage_factor) <= self.max_leverage_factor:
            return True
        else:
            print(
                f"{Utils.dateprint()} - RISK MGMT: La posición objetivo {
                    sizing_event.signal
                } {sizing_event.volume} implica un Leverage Factor de {
                    abs(new_leverage_factor):.2f}, que supera el máx. de {
                    self.max_leverage_factor
                }"
            )
            return False

    def assess_order(
        self,
        sizing_event: SizingEvent,
        current_positions_value_acc_ccy: float,
        new_position_value_acc_ccy: float,
    ) -> float | None:

        if self._check_expected_new_position_is_compliant_with_max_leverage_factor(
            sizing_event, current_positions_value_acc_ccy, new_position_value_acc_ccy
        ):
            return sizing_event.volume
        else:
            return None
