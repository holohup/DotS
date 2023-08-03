from abc import ABC, abstractmethod
from domain.model import generate_buy_order, generate_sell_order, NoMoreOrders, Order
from domain.orderbook import OrderBookDelta, OrderBook


class Trader(ABC):
    def __init__(self, ob_delta: OrderBookDelta, make_broker, take_broker, spread) -> None:
        self._delta = ob_delta
        self._mb = make_broker
        self._tb = take_broker
        self._spread = spread
        self._sell_order: Order = None
        self._buy_order: Order = None
        self._get_orders()

    def _get_orders(self):
        try:
            self._buy_order = generate_buy_order(self._spread)
        except NoMoreOrders:
            self._buy_order = None
        try:
            self._sell_order = generate_sell_order(self._spread)
        except NoMoreOrders:
            self._sell_order = None

    def trade_cycle(self):
        if self._delta.buy_delta <= self._buy_order.price:
            print(f'need to buy {self._delta=}')
        if self._delta.sell_delta >= self._sell_order.price:
            print(f'need to sell {self._delta=}')
