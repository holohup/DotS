from domain.model import (
    generate_buy_order,
    generate_sell_order,
    NoMoreOrders,
    Order,
)
from domain.orderbook import OrderBookDelta
from domain.model import Spread


class Trader:
    def __init__(
        self,
        ob_delta: OrderBookDelta,
        make_broker,
        take_broker,
        spread: Spread,
        next: bool
    ) -> None:
        self._delta = ob_delta
        self._mb = make_broker
        self._tb = take_broker
        self._spread = spread
        self._next = next
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
        print(f'got new orders. {self._buy_order=}, {self._sell_order=}')

    def trade_cycle(self):
        bd = self._delta.buy_delta
        sd = self._delta.sell_delta
        if (
            bd is not None
            and self._buy_order is not None
            and bd <= self._buy_order.price
        ):
            print('buying spread')
            self._buy_spread()
        if (
            sd is not None
            and self._sell_order is not None
            and sd >= self._sell_order.price
        ):
            print('selling spread')
            self._sell_spread()

    def _sell_spread(self):
        amount = self._sell_order.amount
        print(f'{self._next=}')
        print('sell_spread')
        print('buy_maker')
        print('sell_taker * ratio')
        print('update_spread')
        self._spread.update_open_positions(-amount)
        print('get_orders')
        self._get_orders()

    def _buy_spread(self):
        amount = self._buy_order.amount
        print(f'{self._next=}')
        print('buy_spread')
        print('sell_maker')
        print('buy_taker * ratio')
        print('update_spread')
        self._spread.update_open_positions(amount)
        print('get_orders')
        self._get_orders()
