from dataclasses import dataclass
from exceptions import NoMoreOrders
import uuid


@dataclass(frozen=True)
class Order:
    spread_id: str
    sell: bool
    amount: int
    price: float
    order_id: str = 'undefined'

    def __eq__(self, other) -> bool:
        attribs_eq = [
            getattr(self, a) == getattr(other, a)
            for a in ('spread_id', 'sell', 'amount', 'price')
        ]
        return all(attribs_eq) and isinstance(other, Order)


class Spread:
    def __init__(
        self,
        spread_id: str,
        buy_prices: set[int],
        sell_prices: set[int],
        max_amount: int,
        open_positions: int = 0,
    ) -> None:
        self.spread_id = spread_id
        self._buy_prices = list(sorted(buy_prices, reverse=True))
        self._sell_prices = list(sorted(sell_prices))
        self._buy_orders = self._sell_orders = []
        self._max_amount = max_amount
        self._open_positions = open_positions

    def update_open_positions(self, amount):
        if amount == 0:
            return
        self._open_positions += amount

    @property
    def open_positions(self):
        return self._open_positions

    @property
    def max_amount(self):
        return self._max_amount

    @property
    def sell_prices(self):
        return self._sell_prices

    @property
    def buy_prices(self):
        return self._buy_prices


def generate_order_id():
    return str(uuid.uuid4())


def generate_order(spread: Spread, sell: bool) -> Order:
    if sell:
        total_amount = spread.max_amount + spread.open_positions
        prices = spread.sell_prices
    else:
        total_amount = spread.max_amount - spread.open_positions
        prices = spread.buy_prices

    if total_amount >= spread.max_amount:
        amount = total_amount // 2
        price = prices[0]

    else:
        if total_amount < 1:
            raise NoMoreOrders('No more orders.')

        regular_amounts = [spread.max_amount // 2, spread.max_amount // 3]
        regular_amounts.append(spread.max_amount - sum(regular_amounts))
        undistributed_amount = total_amount
        reversed_amounts = []
        for ra in regular_amounts[::-1]:
            amount = min(undistributed_amount, ra)
            reversed_amounts.append(amount)
            undistributed_amount -= amount
        for amount, price in zip(reversed_amounts[::-1], prices):
            if amount > 0:
                break
    return Order(spread.spread_id, sell, amount, price, generate_order_id())
