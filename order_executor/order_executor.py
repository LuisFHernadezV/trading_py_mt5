from operator import imod
from dataclasses import dataclass
from queue import Queue
from portfolio.portfolio import Portfolio
from event.event import ExecutionEvent, OrderEvent, PlacedPendingOrderEvent, SignalType
import MetaTrader5 as mt5
from utils.utils import Utils
from datetime import datetime
import pandas as pd
import time


@dataclass()
class OrderExecutor:
    event_queue: Queue
    portfolio: Portfolio

    def execute_order(self, order_event: OrderEvent) -> None:
        if order_event.target_order == "MARKET":
            # llamamos el método que ejecuta ordenes mercado
            self._execute_market_order(order_event)
        else:
            # llamamos al método que ejecuta ordenes pendientes
            pass

    def cancel_pending_order_by_ticket(self, ticket: int) -> None:
        order = mt5.orders_get(ticket=ticket)[0]

        if order is None:
            print(f"ORD EXEC: No existe ninguna orden pendiente con el ticket {ticket}")
            return None
        cancel_request = {
            "action": mt5.TRADE_ACTION_REMOVE,
            "order": order.ticket,
            "symbol": order.symbol,
        }

        result = mt5.order_send(cancel_request)
        if self._check_execution_status(result):
            print(
                f"Order pendiente con ticket {ticket} en {order.symbol} y volumen {
                    order.volume_initial
                } se ha cancelado correctamente"
            )
        else:
            print(
                f"Ha habido un error al cancelar la orden {ticket} en {
                    order.symbol
                } con volumen {order.volume_initial}: {result.comment}"
            )

    def _send_pending_order(self, order_event: OrderEvent) -> None:
        if order_event.target_order == "STOP":
            order_type = (
                mt5.ORDER_TYPE_BUY_STOP
                if order_event.signal == "BUY"
                else mt5.ORDER_TYPE_SELL_STOP
            )
        elif order_event.target_order == "LIMIT":
            order_type = (
                mt5.ORDER_TYPE_BUY_LIMIT
                if order_event.signal == "BUY"
                else mt5.ORDER_TYPE_SELL_LIMIT
            )
        else:
            raise Exception(
                f"Error: Target order {order_event.target_order} not supported"
            )
        pending_order_request = {
            "action": mt5.TRADE_ACTION_PENDING,
            "symbol": order_event.symbol,
            "volume": order_event.volume,
            "price": order_event.target_price,
            "sl": order_event.stop_loss,
            "tp": order_event.take_profit,
            "type": order_type,
            "deviation": 0,
            "magic": order_event.magic_number,
            "comment": "FWKPending Order",
            "type_filling": mt5.ORDER_FILLING_FOK,
            "type_time": mt5.ORDER_TIME_GTC,
        }
        result = mt5.order_send(pending_order_request)

        if self._check_execution_status(result):
            print(
                f"Pending Order {order_event.signal} {order_event.target_order} para {
                    order_event.symbol
                } de {order_event.volume} lotes colocada en {
                    order_event.target_price
                } correctamente"
            )
            self._create_and_put_placed_pending_order_event(order_event)
        else:
            print(
                f"Pending Order {order_event.signal} {order_event.target_order} para {
                    order_event.symbol
                } de {order_event.volume} lotes colocada en {
                    order_event.target_price
                } correctamente"
            )

    def _execute_market_order(self, order_event: OrderEvent) -> None:
        if order_event.signal == "BUY":
            order_type = mt5.ORDER_TYPE_BUY
        elif order_event.signal == "SELL":
            order_type = mt5.ORDER_TYPE_SELL
        else:
            raise Exception(f"Error: Signal {order_event.signal} not supported")

        market_order_request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": order_event.symbol,
            "volume": order_event.volume,
            "price": mt5.symbol_info(order_event.symbol).bid,
            "sl": order_event.stop_loss,
            "tp": order_event.take_profit,
            "type": order_type,
            "deviation": 0,
            "magic": order_event.magic_number,
            "comment": "FWK Market Order",
            "type_filling": mt5.ORDER_FILLING_FOK,
        }
        result = mt5.order_send(market_order_request)

        if self._check_execution_status(result):
            print(
                f"Market Order {order_event.signal} para {order_event.symbol} de {
                    order_event.volume
                } lotes ejecutada correctamente"
            )
        else:
            print(
                f"Order Executor: Ha habido un error al ejecutar la Market Order {
                    order_event.signal
                } para {order_event.symbol}: {result.comment}"
            )

    def _create_and_put_placed_pending_order_event(
        self, order_event: OrderEvent
    ) -> None:
        """
        Creates a PlacedPendingOrderEvent object based on the given OrderEvent and puts it in the events queue.

        Args:
            order_event (OrderEvent): The OrderEvent object containing the necessary information.

        Returns:
            None
        """
        # Creamos el placed pending order event
        placed_pending_order_event = PlacedPendingOrderEvent(
            symbol=order_event.symbol,
            signal=order_event.signal,
            target_order=order_event.target_order,
            target_price=order_event.target_price,
            magic_number=order_event.magic_number,
            stop_loss=order_event.stop_loss,
            take_profit=order_event.take_profit,
            volume=order_event.volume,
        )

        # Lo colocamos en la events queue
        self.event_queue.put(placed_pending_order_event)

    def _create_and_put_execution_event(self, order_result) -> None:
        """
        Creates an execution event based on the order result and puts it into the events queue.

        Args:
            order_result (OrderResult): The result of the order execution.

        Returns:
            None
        """
        # Obtenemos la información del deal resultado de la ejecución de la orden usando la POSICIÓN a la que el deal pertenece (en lugar del ticket del propio deal),
        # ya que en LIVE el resultado del deal suele ser 0 si lo consultamos inmediatamente.
        # deal = mt5.history_deals_get(ticket=order_result.deal)[0]
        deal = None

        # Simulamos un fill_time usando el momento actual
        fill_time = datetime.now()

        # Creamos un pequeño bucle para dar tiempo al servidor a que genere el deal, y definimos un máximo de 5 intentos
        for _ in range(5):
            # Esperamos 0.5 segundos
            time.sleep(0.5)
            try:
                deal = mt5.history_deals_get(position=order_result.order)[
                    0
                ]  # Usamos position en lugar de ticket
            except IndexError:
                deal = None

            if not deal:
                # Si no obtenemos el deal, vamos a guardar el fill time como "ahora" para tener una aproximación -> puedes modificarlo si lo consideras necesario
                fill_time = datetime.now()
                continue
            else:
                break

        # Si pasado el bucle no hemos obtenido el deal, mostramos un mensaje de error
        if not deal:
            print(
                f"{
                    Utils.dateprint()
                } - ORD EXEC: No se ha podido obtener el deal de la ejecución de la orden {
                    order_result.order
                }, aunque probablemente haya sido ejecutada."
            )

        # Creamos el execution event
        execution_event = ExecutionEvent(
            symbol=order_result.request.symbol,
            signal=SignalType.BUY
            if order_result.request.type == mt5.DEAL_TYPE_BUY
            else SignalType.SELL,
            fill_price=order_result.price,
            fill_time=fill_time
            if not deal
            else pd.to_datetime(deal.time_msc, unit="ms"),
            volume=order_result.request.volume,
        )

        # Colocar el execution event a la cola de eventos
        self.event_queue.put(execution_event)

    def close_position_by_ticket(self, ticket: int) -> None:
        position = mt5.positions_get(ticket=ticket)[0]
        if position is None:
            raise Exception(
                f"ORD EXEC: No existe ninguna posición con el ticket {ticket}"
            )

        close_request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "position": position.ticket,
            "symbol": position.symbol,
            "volume": position.volume,
            "type": mt5.ORDER_TYPE_BUY
            if position.type == mt5.ORDER_TYPE_SELL
            else mt5.ORDER_TYPE_SELL,
            "type_filling": mt5.ORDER_FILLING_FOK,
        }
        result = mt5.order_send(close_request)

        if self._check_execution_status(result):
            print(
                f"Posición con ticket {ticket} en {position.symbol} y volumen {
                    position.volume
                } se ha cerrado correctamente"
            )
            self._create_and_put_execution_event(result)
        else:
            print(
                f"Ha habido un error al cerrar la posición {ticket} en {
                    position.symbol
                } con volumen {position.volume}: {result.comment}"
            )

    def close_strategy_long_positions_by_symbol(self, symbol: str) -> None:
        positions = self.portfolio.get_strategy_open_positions()
        for position in positions:
            if position.symbol == symbol and position.type == mt5.ORDER_TYPE_BUY:
                self.close_position_by_ticket(position.ticket)

    def close_strategy_short_positions_by_symbol(self, symbol: str) -> None:
        positions = self.portfolio.get_strategy_open_positions()
        for position in positions:
            if position.symbol == symbol and position.type == mt5.ORDER_TYPE_SELL:
                self.close_position_by_ticket(position.ticket)

    def _check_execution_status(self, order_result) -> bool:
        if order_result.retcode == mt5.TRADE_RETCODE_DONE:
            return True
        elif order_result.retcode == mt5.TRADE_RETCODE_DONE_PARTIAL:
            return True
        else:
            return False
