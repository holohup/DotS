from dataclasses import dataclass
from exceptions import NoMoreOrders


@dataclass(frozen=True)
class Order:
    spread_id: str
    sell: bool
    amount: int
    price: float


class Spread:
    positions_distribution = [2, 3]

    def __init__(
        self,
        spread_id: str,
        buy_prices: set[int],
        sell_prices: set[int],
        max_amount: int,
        open_positions: int = 0,
    ) -> None:
        self._spread_id = spread_id
        self._buy_prices = list(sorted(buy_prices, reverse=True))
        self._sell_prices = list(sorted(sell_prices))
        self._buy_orders = self._sell_orders = []
        self._max_amount = max_amount
        self._open_positions = open_positions
        self._generate_orders()

    def _generate_orders(self):
        total_sells = self._max_amount + self._open_positions
        total_buys = self._max_amount - self._open_positions
        if self._open_positions >= 0:
            self._sell_orders = self._generate_orders_with_not_lesser_amount(
                self._sell_prices, total_sells, True
            )
            self._buy_orders = self._generate_orders_with_less_amount(
                self._buy_prices, total_buys, False
            )
        else:
            self._buy_orders = self._generate_orders_with_not_lesser_amount(
                self._buy_prices, total_buys, False
            )
            self._sell_orders = self._generate_orders_with_less_amount(
                self._sell_prices, total_sells, True
            )

    def _generate_orders_with_not_lesser_amount(
        self, prices, positions_to_distribute, sell: bool
    ):
        amounts = [
            positions_to_distribute // divider
            for divider in self.positions_distribution
        ]
        distributed = sum(amounts)
        if distributed < positions_to_distribute:
            amounts.append(positions_to_distribute - distributed)
        result = [
            Order(self._spread_id, sell, amount, price)
            for amount, price in zip(amounts, prices)
        ]
        return result

    def _generate_orders_with_less_amount(
        self, prices, positions_to_distribute, sell: bool
    ):
        regular_amounts = [
            self._max_amount // divider
            for divider in self.positions_distribution
        ]
        distributed = sum(regular_amounts)
        if distributed < self._max_amount:
            regular_amounts.append(self._max_amount - distributed)
        reversed_amounts = []
        undistributed_positions = positions_to_distribute
        for ra in regular_amounts[::-1]:
            amount = min(undistributed_positions, ra)
            if amount > 0:
                reversed_amounts.append(amount)
                undistributed_positions -= amount

        reversed_prices = prices[::-1]
        result = [
            Order(self._spread_id, sell, amount, price)
            for amount, price in zip(
                reversed_amounts,
                reversed_prices[: len(reversed_amounts)],
            )
        ][::-1]
        print(result)
        return result

    def generate_sell_order(self):
        try:
            return self._sell_orders.pop(0)
        except IndexError:
            raise NoMoreOrders('No more sell orders.')

    def generate_buy_order(self):
        try:
            return self._buy_orders.pop(0)
        except IndexError:
            raise NoMoreOrders('No more buy orders.')

    def update_open_positions(self, amount):
        if amount == 0:
            return
        self._open_positions += amount
        self._generate_orders()
