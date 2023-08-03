from collections.abc import Iterable
from dataclasses import dataclass

from domain.tools import generate_order_id


class MaxAmountTooSmall(Exception):
    pass


class NoMoreOrders(Exception):
    pass


@dataclass(frozen=True)
class Order:
    spread_id: str
    sell: bool
    amount: int
    price: float
    order_id: str = 'undefined'

    def __eq__(self, other) -> bool:
        if not isinstance(other, Order):
            return False
        attribs_eq = [
            getattr(self, a) == getattr(other, a)
            for a in ('spread_id', 'sell', 'amount', 'price')
        ]
        return all(attribs_eq)

    def __hash__(self) -> int:
        return hash(self.order_id)

    def __repr__(self) -> str:
        sell = 'sell' if self.sell else 'buy'
        return f'{self.spread_id}: {sell} {self.amount} for {self.price}'


class Spread:
    def __init__(
        self,
        spread_id: str,
        buy_prices: Iterable[int],
        sell_prices: Iterable[int],
        max_amount: int,
        open_positions: int = 0,
    ) -> None:
        self.spread_id = spread_id
        self.buy_prices = list(sorted(buy_prices, reverse=True))
        self.sell_prices = list(sorted(sell_prices))
        self.max_amount = max_amount
        self.open_positions = open_positions
        self._validate_fields()

    def update_open_positions(self, amount):
        self.open_positions += amount
        print(
            f'position for {self.spread_id} updated by {amount}, '
            f'{self.open_positions=}'
        )

    def _validate_fields(self):
        if self.max_amount < 3:
            raise MaxAmountTooSmall('Max amount should be > 2')


def generate_sell_order(spread: Spread) -> Order:
    total_amount = spread.max_amount + spread.open_positions
    prices = spread.sell_prices

    amount, price = amount_and_price(spread, total_amount, prices)
    return Order(spread.spread_id, True, amount, price, generate_order_id())


def generate_buy_order(spread: Spread) -> Order:
    total_amount = spread.max_amount - spread.open_positions
    prices = spread.buy_prices

    amount, price = amount_and_price(spread, total_amount, prices)
    return Order(spread.spread_id, False, amount, price, generate_order_id())


def amount_and_price(spread, total_amount, prices):
    if total_amount >= spread.max_amount:
        amount = total_amount // 2
        price = prices[0]
    else:
        if total_amount < 1:
            raise NoMoreOrders('No more orders.')

        amount, price = get_amount_and_price_with_lesser_amount(
            spread.max_amount, total_amount, prices
        )

    return amount, price


def get_amount_and_price_with_lesser_amount(max_amount, total_amount, prices):
    regular_amounts = [max_amount // 2, max_amount // 3]
    regular_amounts.append(max_amount - sum(regular_amounts))
    undistributed_amount = total_amount
    reversed_amounts = []
    for ra in regular_amounts[::-1]:
        a = min(undistributed_amount, ra)
        reversed_amounts.append(a)
        undistributed_amount -= a
    for amount, price in zip(reversed_amounts[::-1], prices):
        if amount > 0:
            break
    return amount, price
