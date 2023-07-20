from dataclasses import dataclass


@dataclass(frozen=True)
class Order:
    spread_id: str
    sell: bool
    amount: int
    price: float


@dataclass(frozen=True)
class TradeLevels:
    levels: list


@dataclass(frozen=True)
class Spread:
    spread_id: str
    buy_levels: TradeLevels
    sell_levels: TradeLevels
    max_amount: int


class OrderFactory:
    def __init__(self, spreads: list[Spread]) -> None:
        self._spreads = spreads

    def next_buy_order(self, spread_id):
        spread = self._get_correct_spread(spread_id)
        return Order(
            spread.spread_id, False, self._get_next_order_amount(spread), 0.0
        )

    def next_sell_order(self, spread_id):
        spread = self._get_correct_spread(spread_id)
        return Order(
            spread.spread_id, True, self._get_next_order_amount(spread), 4.5
        )

    def _get_next_order_amount(self, spread: Spread):
        return spread.max_amount // 2

    def _get_correct_spread(self, spread_id: int) -> Spread:
        for spread in self._spreads:
            if spread.spread_id != spread_id:
                continue
        return spread
