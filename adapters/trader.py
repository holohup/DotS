from domain.model import (
    generate_buy_order,
    generate_sell_order,
    NoMoreOrders,
    Order,
)
from domain.orderbook import OrderBookDelta
from domain.model import Spread
from config import TAKE_TO_MAKE_RATIO


class Trader:
    def __init__(
        self,
        ob_delta: OrderBookDelta,
        make_broker,
        take_broker,
        spread: Spread,
        next: bool,
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
        print(f'got new orders. {self._buy_order}, {self._sell_order}')

    def trade_cycle(self):
        bd = self._delta.buy_delta
        sd = self._delta.sell_delta
        print(
            ' ',
            self._spread.spread_id,
            self._delta.buy_delta,
            self._delta.sell_delta,
            '           ',
            end='\r',
        )
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
        self._mb.buy(amount, self._next)
        self._tb.sell(amount * TAKE_TO_MAKE_RATIO, self._next)
        self._spread.update_open_positions(-amount)
        self._get_orders()

    def _buy_spread(self):
        amount = self._buy_order.amount
        self._mb.sell(amount, self._next)
        self._tb.buy(amount * TAKE_TO_MAKE_RATIO, self._next)
        self._spread.update_open_positions(amount)
        self._get_orders()
