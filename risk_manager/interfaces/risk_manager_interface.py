from typing import Protocol

from event.event import SizingEvent


class IRiskManager(Protocol):
    def assess_order(
        self,
        sizing_event: SizingEvent,
        current_positions_value_acc_ccy: float | None = None,
        new_position_value_acc_ccy: float | None = None,
    ) -> float | None: ...
