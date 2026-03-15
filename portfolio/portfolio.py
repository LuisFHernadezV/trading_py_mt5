import MetaTrader5 as mt5
from dataclasses import dataclass


@dataclass()
class Portfolio:
    magic_number: int

    def get_open_positions(self) -> tuple:
        return mt5.positions_get()

    def get_strategy_open_positions(self) -> tuple:

        return tuple(
            position
            for position in mt5.positions_get()
            if position.magic_number == self.magic_number
        )

    def get_number_of_positions_by_symbol(self, symbol: str) -> dict[str, int]:
        longs = 0
        shorts = 0

        for position in mt5.positions_get(symbol=symbol):
            if position.type == mt5.ORDER_TYPE_BUY:
                longs += 1
            else:
                shorts += 1
        return {"longs": longs, "shorts": shorts}

    def get_number_of_strategy_open_position_by_symbol(
        self, symbol: str
    ) -> dict[str, int]:
        longs = 0
        shorts = 0

        for position in mt5.positions_get(symbol=symbol):
            if position.magic == self.magic_number:
                if position.type == mt5.ORDER_TYPE_BUY:
                    longs += 1
                else:
                    shorts += 1
        return {"longs": longs, "shorts": shorts}
